from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional


class DecisionForm(FlaskForm):
    type_decision = SelectField("Décision", choices=[("validee", "Valider"), ("rejetee", "Rejeter")])
    motif = TextAreaField("Motif / commentaire", validators=[Optional()])
    submit = SubmitField("Enregistrer la décision")


class AutorisationForm(FlaskForm):
    date_debut = DateField("Date de début", validators=[DataRequired()])
    date_fin = DateField("Date de fin", validators=[DataRequired()])
    submit = SubmitField("Générer l'autorisation")
