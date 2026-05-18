from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user

from app.extensions import db
from app.models import (
    Demandeur, BandeFrequence, DemandeAutorisation,
    PieceJointe, Observation
)
from app.utils.permissions import permission_required
from app.utils.references import generate_demande_reference
from app.utils.audit import log_action
from app.utils.workflow import STATUTS_DEMANDE, statuts_suivants, transition_autorisee
from app.utils.files import save_upload
from .forms import DemandeurForm, DemandeForm, PieceJointeForm, ObservationForm, StatutForm


demandes_bp = Blueprint("demandes", __name__)


@demandes_bp.route("/demandeurs")
@permission_required("gerer_demandeurs")
def demandeurs_index():
    demandeurs = Demandeur.query.order_by(Demandeur.date_creation.desc()).all()
    return render_template("demandes/demandeurs_index.html", demandeurs=demandeurs)


@demandes_bp.route("/demandeurs/create", methods=["GET", "POST"])
@permission_required("gerer_demandeurs")
def demandeurs_create():
    form = DemandeurForm()
    if form.validate_on_submit():
        demandeur = Demandeur()
        form.populate_obj(demandeur)
        db.session.add(demandeur)
        db.session.flush()
        log_action("Création demandeur", entite="demandeurs", entite_id=demandeur.id)
        db.session.commit()
        flash("Demandeur enregistré.", "success")
        return redirect(url_for("demandes.demandeurs_index"))
    return render_template("demandes/demandeur_form.html", form=form, title="Enregistrer un demandeur")


@demandes_bp.route("/demandes")
@permission_required("consulter_demande")
def demandes_index():
    q = request.args.get("q", "").strip()
    statut = request.args.get("statut", "").strip()
    query = DemandeAutorisation.query
    if q:
        query = query.filter(DemandeAutorisation.reference.ilike(f"%{q}%"))
    if statut:
        query = query.filter_by(statut=statut)
    demandes = query.order_by(DemandeAutorisation.date_creation.desc()).all()
    return render_template("demandes/index.html", demandes=demandes, q=q, statut=statut, statuts=STATUTS_DEMANDE)


@demandes_bp.route("/demandes/create", methods=["GET", "POST"])
@permission_required("creer_demande")
def demandes_create():
    form = DemandeForm()
    demandeurs = Demandeur.query.order_by(Demandeur.date_creation.desc()).all()
    bandes = BandeFrequence.query.order_by(BandeFrequence.designation.asc()).all()
    form.demandeur_id.choices = [(d.id, d.nom_complet()) for d in demandeurs]
    form.bande_id.choices = [(0, "-- Non précisée --")] + [(b.id, b.designation) for b in bandes]

    if form.validate_on_submit():
        demande = DemandeAutorisation(
            reference=generate_demande_reference(),
            demandeur_id=form.demandeur_id.data,
            bande_id=form.bande_id.data or None,
            creee_par_id=current_user.id,
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
            statut="creee",
        )
        db.session.add(demande)
        db.session.flush()
        log_action("Création demande", demande=demande, entite="demandes_autorisation", entite_id=demande.id, nouveau_statut="creee")
        db.session.commit()
        flash(f"Demande créée avec la référence {demande.reference}.", "success")
        return redirect(url_for("demandes.detail", demande_id=demande.id))
    return render_template("demandes/form.html", form=form, title="Créer une demande")


@demandes_bp.route("/demandes/<int:demande_id>")
@permission_required("consulter_demande")
def detail(demande_id):
    demande = DemandeAutorisation.query.get_or_404(demande_id)
    piece_form = PieceJointeForm()
    obs_form = ObservationForm()
    statut_form = StatutForm()
    statut_form.nouveau_statut.choices = [(s, STATUTS_DEMANDE[s]) for s in statuts_suivants(demande.statut)]
    return render_template(
        "demandes/detail.html",
        demande=demande,
        piece_form=piece_form,
        obs_form=obs_form,
        statut_form=statut_form,
        statuts=STATUTS_DEMANDE,
    )


@demandes_bp.route("/demandes/<int:demande_id>/piece", methods=["POST"])
@permission_required("ajouter_piece")
def add_piece(demande_id):
    demande = DemandeAutorisation.query.get_or_404(demande_id)
    form = PieceJointeForm()
    if form.validate_on_submit():
        original, stored, path = save_upload(form.fichier.data)
        piece = PieceJointe(
            demande_id=demande.id,
            ajoutee_par_id=current_user.id,
            nom_original=original,
            nom_stockage=stored,
            type_document=form.type_document.data,
            chemin=path,
            mime_type=form.fichier.data.mimetype,
            taille_octets=0,
        )
        db.session.add(piece)
        log_action("Ajout pièce jointe", demande=demande, entite="pieces_jointes")
        db.session.commit()
        flash("Pièce jointe ajoutée.", "success")
    else:
        flash("Erreur lors de l'ajout de la pièce jointe.", "danger")
    return redirect(url_for("demandes.detail", demande_id=demande.id))


@demandes_bp.route("/demandes/<int:demande_id>/observation", methods=["POST"])
@permission_required("ajouter_observation")
def add_observation(demande_id):
    demande = DemandeAutorisation.query.get_or_404(demande_id)
    form = ObservationForm()
    if form.validate_on_submit():
        observation = Observation(
            demande_id=demande.id,
            auteur_id=current_user.id,
            type_observation=form.type_observation.data,
            contenu=form.contenu.data,
        )
        db.session.add(observation)
        log_action("Ajout observation", demande=demande, entite="observations")
        db.session.commit()
        flash("Observation ajoutée.", "success")
    return redirect(url_for("demandes.detail", demande_id=demande.id))


@demandes_bp.route("/demandes/<int:demande_id>/statut", methods=["POST"])
@permission_required("verifier_dossier")
def change_statut(demande_id):
    demande = DemandeAutorisation.query.get_or_404(demande_id)
    form = StatutForm()
    form.nouveau_statut.choices = [(s, STATUTS_DEMANDE[s]) for s in statuts_suivants(demande.statut)]
    if form.validate_on_submit():
        ancien = demande.statut
        nouveau = form.nouveau_statut.data
        if not transition_autorisee(ancien, nouveau):
            flash("Transition de statut non autorisée.", "danger")
            return redirect(url_for("demandes.detail", demande_id=demande.id))
        demande.changer_statut(nouveau)
        demande.dossier_complet = nouveau == "prete_decision"
        log_action("Changement statut demande", demande=demande, ancien_statut=ancien, nouveau_statut=nouveau, commentaire=form.commentaire.data)
        db.session.commit()
        flash("Statut modifié.", "success")
    return redirect(url_for("demandes.detail", demande_id=demande.id))
