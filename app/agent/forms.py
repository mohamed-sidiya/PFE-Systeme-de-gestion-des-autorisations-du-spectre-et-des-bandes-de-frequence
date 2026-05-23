from flask_wtf import FlaskForm
from wtforms import TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional

class ObservationForm(FlaskForm):
    contenu = TextAreaField("Observation", validators=[DataRequired()])
    submit = SubmitField("Ajouter l'observation")

class ComplementRequestForm(FlaskForm):
    motif = TextAreaField("Motif du complément demandé", validators=[DataRequired()])
    submit = SubmitField("Demander un complément")

class DecisionForm(FlaskForm):
    motif = TextAreaField("Motif / commentaire", validators=[Optional()])
    submit = SubmitField("Confirmer")

class AutorisationForm(FlaskForm):
    date_debut = DateField("Date de début", validators=[DataRequired()])
    date_fin = DateField("Date de fin", validators=[DataRequired()])
    submit = SubmitField("Générer l'autorisation")
