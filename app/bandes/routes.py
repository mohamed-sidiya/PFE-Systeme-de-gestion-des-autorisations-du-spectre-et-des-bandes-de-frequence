from flask import Blueprint, render_template, redirect, url_for, flash
from sqlalchemy import select

from app.extensions import db
from app.models import BandeFrequence
from app.utils.constants import ROLE_ADMIN, ROLE_AGENT
from app.utils.decorators import role_required
from app.utils.audit import log_action
from .forms import BandeForm

bandes_bp = Blueprint("bandes", __name__, url_prefix="/bandes")

@bandes_bp.route("/")
@role_required(ROLE_ADMIN, ROLE_AGENT)
def index():
    bandes = db.session.scalars(select(BandeFrequence).order_by(BandeFrequence.frequence_debut.asc())).all()
    return render_template("bandes/index.html", bandes=bandes)

@bandes_bp.route("/create", methods=["GET", "POST"])
@role_required(ROLE_ADMIN)
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
        log_action("Création bande", entite="bandes_frequence", entite_id=bande.id)
        db.session.commit()
        flash("Bande créée.", "success")
        return redirect(url_for("bandes.index"))
    return render_template("bandes/form.html", form=form, title="Créer une bande")

@bandes_bp.route("/<int:bande_id>/edit", methods=["GET", "POST"])
@role_required(ROLE_ADMIN)
def edit(bande_id):
    bande = db.get_or_404(BandeFrequence, bande_id)
    form = BandeForm(obj=bande)
    if form.validate_on_submit():
        form.populate_obj(bande)
        log_action("Modification bande", entite="bandes_frequence", entite_id=bande.id)
        db.session.commit()
        flash("Bande modifiée.", "success")
        return redirect(url_for("bandes.index"))
    return render_template("bandes/form.html", form=form, title="Modifier une bande")
