from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import current_user
from sqlalchemy import select

from app.extensions import db
from app.models import DemandeAutorisation, Observation, Decision, Autorisation, Facture
from app.utils.constants import ROLE_AGENT
from app.utils.decorators import role_required
from app.utils.audit import log_action
from app.utils.references import generate_autorisation_number, generate_facture_number
from app.utils.billing import build_facture_amounts
from .forms import ObservationForm, ComplementRequestForm, DecisionForm, AutorisationForm

agent_bp = Blueprint("agent", __name__, url_prefix="/agent")


@agent_bp.route("/dashboard")
@role_required(ROLE_AGENT)
def dashboard():
    demandes = db.session.scalars(
        select(DemandeAutorisation).order_by(DemandeAutorisation.date_creation.desc()).limit(20)
    ).all()
    return render_template("agent/dashboard.html", demandes=demandes)


@agent_bp.route("/demandes")
@role_required(ROLE_AGENT)
def demandes():
    items = db.session.scalars(select(DemandeAutorisation).order_by(DemandeAutorisation.date_creation.desc())).all()
    return render_template("agent/demandes.html", demandes=items)


@agent_bp.route("/demandes/<int:demande_id>")
@role_required(ROLE_AGENT)
def detail_demande(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    return render_template(
        "agent/demande_detail.html",
        demande=demande,
        observation_form=ObservationForm(),
        complement_form=ComplementRequestForm(),
        decision_form=DecisionForm(),
        autorisation_form=AutorisationForm(),
    )


@agent_bp.route("/demandes/<int:demande_id>/traiter", methods=["POST"])
@role_required(ROLE_AGENT)
def traiter(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if demande.statut not in ["soumise", "completee"]:
        flash("Cette demande ne peut pas passer en traitement.", "warning")
        return redirect(url_for("agent.detail_demande", demande_id=demande.id))
    old = demande.statut
    demande.changer_statut("en_traitement")
    log_action("Prise en traitement", demande=demande, ancien_statut=old, nouveau_statut="en_traitement")
    db.session.commit()
    flash("Demande prise en traitement.", "success")
    return redirect(url_for("agent.detail_demande", demande_id=demande.id))


@agent_bp.route("/demandes/<int:demande_id>/observation", methods=["POST"])
@role_required(ROLE_AGENT)
def observation(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    form = ObservationForm()
    if form.validate_on_submit():
        db.session.add(Observation(
            demande_id=demande.id,
            auteur_id=current_user.id,
            type_observation="agent",
            contenu=form.contenu.data,
        ))
        log_action("Ajout observation agent", demande=demande)
        db.session.commit()
        flash("Observation ajoutee.", "success")
    return redirect(url_for("agent.detail_demande", demande_id=demande.id))


@agent_bp.route("/demandes/<int:demande_id>/complement", methods=["POST"])
@role_required(ROLE_AGENT)
def demander_complement(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    form = ComplementRequestForm()
    if demande.statut != "en_traitement":
        flash("La demande doit etre en traitement.", "warning")
        return redirect(url_for("agent.detail_demande", demande_id=demande.id))
    if form.validate_on_submit():
        old = demande.statut
        demande.changer_statut("complement_demande")
        db.session.add(Observation(
            demande_id=demande.id,
            auteur_id=current_user.id,
            type_observation="demande_complement",
            contenu=form.motif.data,
        ))
        log_action("Demande complement", demande=demande, ancien_statut=old, nouveau_statut="complement_demande", commentaire=form.motif.data)
        db.session.commit()
        flash("Complement demande a l'utilisateur.", "success")
    return redirect(url_for("agent.detail_demande", demande_id=demande.id))


@agent_bp.route("/demandes/<int:demande_id>/facture", methods=["POST"])
@role_required(ROLE_AGENT)
def generer_facture(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    if demande.statut != "en_traitement":
        flash("La demande doit etre en traitement avant de generer une facture.", "warning")
        return redirect(url_for("agent.detail_demande", demande_id=demande.id))
    if demande.facture:
        flash("Une facture existe deja pour cette demande.", "info")
        return redirect(url_for("agent.facture_detail", facture_id=demande.facture.id))

    facture = Facture(
        numero_facture=generate_facture_number(),
        demande_id=demande.id,
        creee_par_id=current_user.id,
        **build_facture_amounts(demande),
    )
    db.session.add(facture)
    log_action("Generation facture", demande=demande, entite="factures")
    db.session.commit()
    flash("Facture generee. La demande peut maintenant etre validee.", "success")
    return redirect(url_for("agent.facture_detail", facture_id=facture.id))


@agent_bp.route("/factures/<int:facture_id>")
@role_required(ROLE_AGENT)
def facture_detail(facture_id):
    facture = db.get_or_404(Facture, facture_id)
    return render_template("agent/facture.html", facture=facture)


@agent_bp.route("/demandes/<int:demande_id>/valider", methods=["POST"])
@role_required(ROLE_AGENT)
def valider(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    form = DecisionForm()
    if demande.statut != "en_traitement":
        flash("La demande doit etre en traitement.", "warning")
        return redirect(url_for("agent.detail_demande", demande_id=demande.id))
    if not demande.facture:
        flash("Generez la facture avant de valider la demande.", "warning")
        return redirect(url_for("agent.detail_demande", demande_id=demande.id))
    if demande.facture.statut != "payee":
        flash("La facture doit etre payee avant de valider la demande.", "warning")
        return redirect(url_for("agent.detail_demande", demande_id=demande.id))
    if form.validate_on_submit():
        old = demande.statut
        demande.changer_statut("validee")
        db.session.add(Decision(
            demande_id=demande.id,
            agent_id=current_user.id,
            type_decision="validee",
            motif=form.motif.data,
        ))
        log_action("Validation demande", demande=demande, ancien_statut=old, nouveau_statut="validee", commentaire=form.motif.data)
        db.session.commit()
        flash("Demande validee.", "success")
    return redirect(url_for("agent.detail_demande", demande_id=demande.id))


@agent_bp.route("/demandes/<int:demande_id>/rejeter", methods=["POST"])
@role_required(ROLE_AGENT)
def rejeter(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    form = DecisionForm()
    if demande.statut != "en_traitement":
        flash("La demande doit etre en traitement.", "warning")
        return redirect(url_for("agent.detail_demande", demande_id=demande.id))
    if form.validate_on_submit():
        old = demande.statut
        demande.changer_statut("rejetee")
        db.session.add(Decision(
            demande_id=demande.id,
            agent_id=current_user.id,
            type_decision="rejetee",
            motif=form.motif.data,
        ))
        log_action("Rejet demande", demande=demande, ancien_statut=old, nouveau_statut="rejetee", commentaire=form.motif.data)
        db.session.commit()
        flash("Demande rejetee.", "info")
    return redirect(url_for("agent.detail_demande", demande_id=demande.id))


@agent_bp.route("/demandes/<int:demande_id>/autorisation", methods=["POST"])
@role_required(ROLE_AGENT)
def generer_autorisation(demande_id):
    demande = db.get_or_404(DemandeAutorisation, demande_id)
    form = AutorisationForm()
    if not demande.facture or demande.facture.statut != "payee":
        flash("L'autorisation ne peut etre generee qu'apres paiement de la facture.", "warning")
        return redirect(url_for("agent.detail_demande", demande_id=demande.id))
    if not demande.peut_generer_autorisation():
        flash("L'autorisation ne peut etre generee que pour une demande validee.", "warning")
        return redirect(url_for("agent.detail_demande", demande_id=demande.id))
    if form.validate_on_submit():
        old = demande.statut
        autorisation = Autorisation(
            demande_id=demande.id,
            bande_id=demande.bande_id,
            creee_par_id=current_user.id,
            numero_autorisation=generate_autorisation_number(),
            date_debut=form.date_debut.data,
            date_fin=form.date_fin.data,
            statut="active",
        )
        demande.changer_statut("autorisation_generee")
        db.session.add(autorisation)
        log_action("Generation autorisation", demande=demande, ancien_statut=old, nouveau_statut="autorisation_generee")
        db.session.commit()
        flash("Autorisation generee.", "success")
    return redirect(url_for("agent.detail_demande", demande_id=demande.id))


@agent_bp.route("/autorisations/<int:autorisation_id>/document")
@role_required(ROLE_AGENT)
def autorisation_document(autorisation_id):
    autorisation = db.get_or_404(Autorisation, autorisation_id)
    return render_template("agent/autorisation_document.html", autorisation=autorisation)
