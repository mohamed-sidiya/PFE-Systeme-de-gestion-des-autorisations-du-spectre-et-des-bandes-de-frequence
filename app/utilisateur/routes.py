from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, send_file
from flask_login import current_user
from sqlalchemy import select

from app.extensions import db
from app.models import DemandeAutorisation, BandeFrequence, PieceJointe, Observation
from app.utils.constants import ROLE_UTILISATEUR
from app.utils.decorators import role_required, validated_account_required
from app.utils.references import generate_demande_reference
from app.utils.audit import log_action
from app.utils.files import save_upload
from app.utils.pdf import build_facture_pdf, build_autorisation_pdf
from .forms import DemandeForm, ComplementForm

utilisateur_bp = Blueprint("utilisateur", __name__, url_prefix="/utilisateur")


def fill_bandes_choices(form):
    bandes = db.session.scalars(select(BandeFrequence).order_by(BandeFrequence.frequence_debut.asc())).all()
    form.bande_id.choices = [(0, "Non precisee")] + [
        (b.id, f"{b.designation} ({b.frequence_debut}-{b.frequence_fin} {b.unite})")
        for b in bandes
    ]
    return bandes


def build_bande_limits(bandes):
    return [
        {
            "id": b.id,
            "min": str(b.frequence_debut),
            "max": str(b.frequence_fin),
            "unite": b.unite,
        }
        for b in bandes
    ]


def add_field_error(field, message):
    field.errors = list(field.errors) + [message]


def validate_frequence_bounds(form):
    if form.frequence_min.data is not None and form.frequence_max.data is not None and form.frequence_min.data > form.frequence_max.data:
        add_field_error(form.frequence_max, "La frequence maximale doit etre superieure ou egale a la frequence minimale.")
        return None

    if not form.bande_id.data:
        return None

    bande = db.session.get(BandeFrequence, form.bande_id.data)
    if not bande:
        add_field_error(form.bande_id, "Bande de frequence invalide.")
        return None

    if form.frequence_min.data is not None and form.frequence_min.data < bande.frequence_debut:
        add_field_error(form.frequence_min, f"La frequence minimale ne peut pas etre inferieure a {bande.frequence_debut} {bande.unite}.")
    if form.frequence_max.data is not None and form.frequence_max.data > bande.frequence_fin:
        add_field_error(form.frequence_max, f"La frequence maximale ne peut pas etre superieure a {bande.frequence_fin} {bande.unite}.")
    if form.frequence_min.errors or form.frequence_max.errors:
        return None

    return bande


@utilisateur_bp.route("/dashboard")
@role_required(ROLE_UTILISATEUR)
@validated_account_required
def dashboard():
    demandes = db.session.scalars(
        select(DemandeAutorisation).where(DemandeAutorisation.utilisateur_id == current_user.id).order_by(DemandeAutorisation.date_creation.desc())
    ).all()
    return render_template("utilisateur/dashboard.html", demandes=demandes)


@utilisateur_bp.route("/demandes")
@role_required(ROLE_UTILISATEUR)
@validated_account_required
def demandes():
    items = db.session.scalars(
        select(DemandeAutorisation).where(DemandeAutorisation.utilisateur_id == current_user.id).order_by(DemandeAutorisation.date_creation.desc())
    ).all()
    return render_template("utilisateur/demandes.html", demandes=items)


@utilisateur_bp.route("/demandes/nouvelle", methods=["GET", "POST"])
@role_required(ROLE_UTILISATEUR)
@validated_account_required
def nouvelle_demande():
    form = DemandeForm()
    bandes = fill_bandes_choices(form)
    bande_limits = build_bande_limits(bandes)
    if form.validate_on_submit():
        bande = validate_frequence_bounds(form)
        if form.errors:
            return render_template("utilisateur/demande_form.html", form=form, bande_limits=bande_limits)

        demande = DemandeAutorisation(
            reference=generate_demande_reference(),
            utilisateur_id=current_user.id,
            bande_id=form.bande_id.data or None,
            objet=form.objet.data,
            type_demande=form.type_demande.data,
            service_concerne=form.service_concerne.data,
            frequence_min=form.frequence_min.data,
            frequence_max=form.frequence_max.data,
            unite=bande.unite if bande else form.unite.data,
            zone_utilisation=form.zone_utilisation.data,
            puissance=form.puissance.data or None,
            date_debut_souhaitee=form.date_debut_souhaitee.data,
            date_fin_souhaitee=form.date_fin_souhaitee.data,
            statut="soumise",
            date_soumission=datetime.utcnow(),
        )
        db.session.add(demande)
        db.session.flush()
        try:
            saved = save_upload(form.document_requis.data)
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
            return render_template("utilisateur/demande_form.html", form=form, bande_limits=bande_limits)

        db.session.add(PieceJointe(
            demande_id=demande.id,
            ajoutee_par_id=current_user.id,
            type_document="Document joint",
            **saved,
        ))
        log_action("Soumission demande", demande=demande, nouveau_statut="soumise")
        db.session.commit()
        flash("Demande soumise avec succes.", "success")
        return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))
    return render_template("utilisateur/demande_form.html", form=form, bande_limits=bande_limits)


@utilisateur_bp.route("/demandes/<int:demande_id>")
@role_required(ROLE_UTILISATEUR)
@validated_account_required
def detail_demande(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if demande.utilisateur_id != current_user.id:
        flash("Acces interdit.", "danger")
        return redirect(url_for("utilisateur.demandes"))
    return render_template("utilisateur/demande_detail.html", demande=demande, complement_form=ComplementForm())


@utilisateur_bp.route("/demandes/<int:demande_id>/payer", methods=["POST"])
@role_required(ROLE_UTILISATEUR)
@validated_account_required
def payer_facture(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if demande.utilisateur_id != current_user.id:
        flash("Acces interdit.", "danger")
        return redirect(url_for("utilisateur.demandes"))
    if not demande.facture:
        flash("Aucune facture n'a ete generee pour cette demande.", "warning")
        return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))
    if demande.facture.statut == "payee":
        flash("Cette facture est deja payee.", "info")
        return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))

    demande.facture.statut = "payee"
    demande.facture.date_paiement = datetime.utcnow()
    demande.facture.payee_par_id = current_user.id
    log_action("Paiement facture", demande=demande, entite="factures", entite_id=demande.facture.id)
    db.session.commit()
    flash("Paiement enregistre. L'agent peut maintenant generer l'autorisation.", "success")
    return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))


@utilisateur_bp.route("/demandes/<int:demande_id>/facture.pdf")
@role_required(ROLE_UTILISATEUR)
@validated_account_required
def facture_pdf(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if demande.utilisateur_id != current_user.id:
        flash("Acces interdit.", "danger")
        return redirect(url_for("utilisateur.demandes"))
    if not demande.facture:
        flash("Aucune facture n'a ete generee pour cette demande.", "warning")
        return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))

    pdf = build_facture_pdf(demande.facture)
    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{demande.facture.numero_facture}.pdf",
    )


@utilisateur_bp.route("/demandes/<int:demande_id>/autorisation.pdf")
@role_required(ROLE_UTILISATEUR)
@validated_account_required
def autorisation_pdf(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if demande.utilisateur_id != current_user.id:
        flash("Acces interdit.", "danger")
        return redirect(url_for("utilisateur.demandes"))
    if not demande.autorisation:
        flash("Aucune autorisation n'a ete generee pour cette demande.", "warning")
        return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))

    pdf = build_autorisation_pdf(demande.autorisation)
    return send_file(
        pdf,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{demande.autorisation.numero_autorisation}.pdf",
    )


@utilisateur_bp.route("/demandes/<int:demande_id>/completer", methods=["POST"])
@role_required(ROLE_UTILISATEUR)
@validated_account_required
def completer(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if demande.utilisateur_id != current_user.id or demande.statut != "complement_demande":
        flash("Action non autorisee.", "danger")
        return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))
    form = ComplementForm()
    if form.validate_on_submit():
        old = demande.statut
        demande.changer_statut("completee")
        observation = Observation(
            demande_id=demande.id,
            auteur_id=current_user.id,
            type_observation="complement",
            contenu=form.commentaire.data,
        )
        db.session.add(observation)
        if form.fichier.data:
            try:
                saved = save_upload(form.fichier.data)
                db.session.add(PieceJointe(
                    demande_id=demande.id,
                    ajoutee_par_id=current_user.id,
                    type_document="complement",
                    **saved
                ))
            except ValueError as exc:
                flash(str(exc), "danger")
                return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))
        log_action("Complement fourni", demande=demande, ancien_statut=old, nouveau_statut="completee")
        db.session.commit()
        flash("Complement envoye.", "success")
    return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))
