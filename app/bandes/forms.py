from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class BandeForm(FlaskForm):
    designation = StringField("Désignation", validators=[DataRequired(), Length(max=150)])
    frequence_debut = DecimalField("Fréquence début", places=3, validators=[DataRequired()])
    frequence_fin = DecimalField("Fréquence fin", places=3, validators=[DataRequired()])
    unite = SelectField("Unité", choices=[("kHz", "kHz"), ("MHz", "MHz"), ("GHz", "GHz")], default="MHz")
    usage_service = StringField("Usage / service associé", validators=[Optional(), Length(max=150)])
    statut = SelectField("Statut", choices=[
        ("reference", "Référence TNABF"),
        ("a_verifier", "À vérifier"),
        ("reservee", "Réservée"),
        ("occupee", "Occupée"),
    ], default="reference")
    description = TextAreaField("Description", validators=[Optional()])
    submit = SubmitField("Enregistrer")
