from datetime import date, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import current_user
from sqlalchemy import select

from app.extensions import db
from app.models import DemandeAutorisation, Decision, Autorisation
from app.utils.permissions import permission_required, any_permission_required
from app.utils.references import generate_autorisation_number
from app.utils.audit import log_action
from .forms import DecisionForm, AutorisationForm


autorisations_bp = Blueprint("autorisations", __name__)


@autorisations_bp.route("/autorisations")
@permission_required("consulter_demande")
def index():
    autorisations = db.session.scalars(
        select(Autorisation).order_by(Autorisation.date_creation.desc())
    ).all()
    return render_template("autorisations/index.html", autorisations=autorisations)


@autorisations_bp.route("/demandes/<int:demande_id>/decider", methods=["GET", "POST"])
@any_permission_required("valider_demande", "rejeter_demande")
def decider(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if demande.statut != "prete_decision":
        flash("La demande doit être au statut 'Prête à décision'.", "warning")
        return redirect(url_for("demandes.detail", demande_id=demande.id))

    form = DecisionForm()
    choices = []
    if current_user.can("valider_demande"):
        choices.append(("validee", "Valider"))
    if current_user.can("rejeter_demande"):
        choices.append(("rejetee", "Rejeter"))
    form.type_decision.choices = choices

    if form.validate_on_submit():
        if form.type_decision.data == "validee" and not current_user.can("valider_demande"):
            abort(403)
        if form.type_decision.data == "rejetee" and not current_user.can("rejeter_demande"):
            abort(403)

        ancien = demande.statut
        decision = Decision(
            demande_id=demande.id,
            responsable_id=current_user.id,
            type_decision=form.type_decision.data,
            motif=form.motif.data,
        )
        demande.changer_statut(form.type_decision.data)
        db.session.add(decision)
        log_action(
            "Décision finale",
            demande=demande,
            ancien_statut=ancien,
            nouveau_statut=demande.statut,
            commentaire=form.motif.data,
        )

        if form.type_decision.data == "validee" and demande.autorisation is None:
            date_debut = demande.date_debut_souhaitee or date.today()
            date_fin = demande.date_fin_souhaitee or (date_debut + timedelta(days=365))
            autorisation = Autorisation(
                demande_id=demande.id,
                bande_id=demande.bande_id,
                creee_par_id=current_user.id,
                numero_autorisation=generate_autorisation_number(),
                date_debut=date_debut,
                date_fin=date_fin,
                statut="active",
                document_url=None,
            )
            db.session.add(autorisation)
            log_action(
                "Génération autorisation",
                demande=demande,
                ancien_statut=ancien,
                nouveau_statut="validee",
            )

        db.session.commit()
        if form.type_decision.data == "validee":
            flash("Décision favorable enregistrée et autorisation générée.", "success")
        else:
            flash("Décision de rejet enregistrée.", "success")
        return redirect(url_for("demandes.detail", demande_id=demande.id))
    return render_template("autorisations/decision_form.html", form=form, demande=demande)


@autorisations_bp.route("/demandes/<int:demande_id>/generer", methods=["GET", "POST"])
@permission_required("generer_autorisation")
def generer(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if not demande.peut_generer_autorisation():
        flash("L'autorisation ne peut être générée que pour une demande validée sans autorisation existante.", "warning")
        return redirect(url_for("demandes.detail", demande_id=demande.id))

    form = AutorisationForm()
    if form.validate_on_submit():
        autorisation = Autorisation(
            demande_id=demande.id,
            bande_id=demande.bande_id,
            creee_par_id=current_user.id,
            numero_autorisation=generate_autorisation_number(),
            date_debut=form.date_debut.data,
            date_fin=form.date_fin.data,
            statut="active",
            document_url=None,
        )
        db.session.add(autorisation)
        log_action("Génération autorisation", demande=demande, ancien_statut=demande.statut, nouveau_statut=demande.statut)
        db.session.commit()
        flash("Autorisation générée.", "success")
        return redirect(url_for("autorisations.index"))
    return render_template("autorisations/autorisation_form.html", form=form, demande=demande)
