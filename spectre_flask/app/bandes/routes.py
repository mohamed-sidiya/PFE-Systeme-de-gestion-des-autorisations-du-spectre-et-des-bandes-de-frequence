from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy import select

from app.extensions import db
from app.models import BandeFrequence
from app.utils.permissions import permission_required
from app.utils.audit import log_action
from .forms import BandeForm


bandes_bp = Blueprint("bandes", __name__, url_prefix="/bandes")


@bandes_bp.route("/")
@permission_required("gerer_bandes")
def index():
    q = request.args.get("q", "").strip()
    stmt = select(BandeFrequence)
    if q:
        stmt = stmt.where(BandeFrequence.designation.ilike(f"%{q}%"))
    bandes = db.session.scalars(stmt.order_by(BandeFrequence.designation.asc())).all()
    return render_template("bandes/index.html", bandes=bandes, q=q)


@bandes_bp.route("/create", methods=["GET", "POST"])
@permission_required("gerer_bandes")
def create():
    form = BandeForm()
    if form.validate_on_submit():
        bande = BandeFrequence(
            designation=form.designation.data,
            frequence_debut=form.frequence_debut.data,
            frequence_fin=form.frequence_fin.data,
            unite=form.unite.data,
            usage_service=form.usage_service.data,
            statut=form.statut.data,
            description=form.description.data,
        )
        db.session.add(bande)
        db.session.flush()
        log_action("Création bande de fréquence", entite="bandes_frequence", entite_id=bande.id)
        db.session.commit()
        flash("Bande de fréquence créée.", "success")
        return redirect(url_for("bandes.index"))
    return render_template("bandes/form.html", form=form, title="Créer une bande")


@bandes_bp.route("/<int:bande_id>/edit", methods=["GET", "POST"])
@permission_required("gerer_bandes")
def edit(bande_id):
    bande = db.get_or_404(BandeFrequence, bande_id)
    form = BandeForm(obj=bande)
    if form.validate_on_submit():
        form.populate_obj(bande)
        log_action("Modification bande de fréquence", entite="bandes_frequence", entite_id=bande.id)
        db.session.commit()
        flash("Bande de fréquence modifiée.", "success")
        return redirect(url_for("bandes.index"))
    return render_template("bandes/form.html", form=form, title="Modifier une bande")
