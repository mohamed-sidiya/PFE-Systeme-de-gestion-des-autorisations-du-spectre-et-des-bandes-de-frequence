from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user
from sqlalchemy import select

from app.extensions import db
from app.models import DemandeAutorisation, BandeFrequence, PieceJointe, Observation
from app.utils.constants import ROLE_UTILISATEUR
from app.utils.decorators import role_required, validated_account_required
from app.utils.references import generate_demande_reference
from app.utils.audit import log_action
from app.utils.files import save_upload
from .forms import DemandeForm, PieceForm, ComplementForm

utilisateur_bp = Blueprint("utilisateur", __name__, url_prefix="/utilisateur")

def fill_bandes_choices(form):
    bandes = db.session.scalars(select(BandeFrequence).order_by(BandeFrequence.frequence_debut.asc())).all()
    form.bande_id.choices = [(0, "Non précisée")] + [(b.id, f"{b.designation} ({b.frequence_debut}-{b.frequence_fin} {b.unite})") for b in bandes]

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
    fill_bandes_choices(form)
    if form.validate_on_submit():
        demande = DemandeAutorisation(
            reference=generate_demande_reference(),
            utilisateur_id=current_user.id,
            bande_id=form.bande_id.data or None,
            objet=form.objet.data,
            type_demande=form.type_demande.data,
            service_concerne=form.service_concerne.data,
            frequence_min=form.frequence_min.data,
            frequence_max=form.frequence_max.data,
            unite=form.unite.data,
            zone_utilisation=form.zone_utilisation.data,
            puissance=form.puissance.data,
            date_debut_souhaitee=form.date_debut_souhaitee.data,
            date_fin_souhaitee=form.date_fin_souhaitee.data,
            description=form.description.data,
            statut="soumise",
            date_soumission=datetime.utcnow(),
        )
        db.session.add(demande)
        db.session.flush()
        log_action("Soumission demande", demande=demande, nouveau_statut="soumise")
        db.session.commit()
        flash("Demande soumise avec succès.", "success")
        return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))
    return render_template("utilisateur/demande_form.html", form=form)

@utilisateur_bp.route("/demandes/<int:demande_id>")
@role_required(ROLE_UTILISATEUR)
@validated_account_required
def detail_demande(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if demande.utilisateur_id != current_user.id:
        flash("Accès interdit.", "danger")
        return redirect(url_for("utilisateur.demandes"))
    return render_template("utilisateur/demande_detail.html", demande=demande, piece_form=PieceForm(), complement_form=ComplementForm())

@utilisateur_bp.route("/demandes/<int:demande_id>/piece", methods=["POST"])
@role_required(ROLE_UTILISATEUR)
@validated_account_required
def ajouter_piece(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if demande.utilisateur_id != current_user.id:
        flash("Accès interdit.", "danger")
        return redirect(url_for("utilisateur.demandes"))
    form = PieceForm()
    if form.validate_on_submit():
        try:
            saved = save_upload(form.fichier.data)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))
        piece = PieceJointe(
            demande_id=demande.id,
            ajoutee_par_id=current_user.id,
            type_document=form.type_document.data,
            **saved
        )
        db.session.add(piece)
        log_action("Ajout pièce jointe", demande=demande)
        db.session.commit()
        flash("Pièce jointe ajoutée.", "success")
    return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))

@utilisateur_bp.route("/demandes/<int:demande_id>/completer", methods=["POST"])
@role_required(ROLE_UTILISATEUR)
@validated_account_required
def completer(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if demande.utilisateur_id != current_user.id or demande.statut != "complement_demande":
        flash("Action non autorisée.", "danger")
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
                    type_document="complément",
                    **saved
                ))
            except ValueError as exc:
                flash(str(exc), "danger")
                return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))
        log_action("Complément fourni", demande=demande, ancien_statut=old, nouveau_statut="completee")
        db.session.commit()
        flash("Complément envoyé.", "success")
    return redirect(url_for("utilisateur.detail_demande", demande_id=demande.id))
