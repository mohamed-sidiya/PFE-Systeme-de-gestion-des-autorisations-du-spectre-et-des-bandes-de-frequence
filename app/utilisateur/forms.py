from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DecimalField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class DemandeForm(FlaskForm):
    bande_id = SelectField("Bande de fréquence", coerce=int, validators=[Optional()])
    objet = StringField("Objet", validators=[DataRequired(), Length(max=255)])
    type_demande = SelectField("Type de demande", choices=[
        ("nouvelle", "Nouvelle demande"),
        ("renouvellement", "Renouvellement"),
        ("modification", "Modification"),
    ])
    service_concerne = StringField("Service concerné", validators=[Optional(), Length(max=150)])
    frequence_min = DecimalField("Fréquence minimale", places=3, validators=[Optional()])
    frequence_max = DecimalField("Fréquence maximale", places=3, validators=[Optional()])
    unite = SelectField("Unité", choices=[("kHz", "kHz"), ("MHz", "MHz"), ("GHz", "GHz")], default="MHz")
    zone_utilisation = StringField("Zone d'utilisation", validators=[Optional(), Length(max=255)])
    puissance = DecimalField("Puissance", places=2, validators=[Optional()])
    date_debut_souhaitee = DateField("Date début souhaitée", validators=[Optional()])
    date_fin_souhaitee = DateField("Date fin souhaitée", validators=[Optional()])
    description = TextAreaField("Description", validators=[Optional()])
    submit = SubmitField("Soumettre la demande")

class PieceForm(FlaskForm):
    type_document = StringField("Type de document", validators=[Optional(), Length(max=100)])
    fichier = FileField("Fichier", validators=[DataRequired(), FileAllowed(["pdf", "png", "jpg", "jpeg", "doc", "docx"])])
    submit = SubmitField("Ajouter")

class ComplementForm(FlaskForm):
    commentaire = TextAreaField("Réponse au complément", validators=[DataRequired()])
    fichier = FileField("Fichier complémentaire", validators=[Optional(), FileAllowed(["pdf", "png", "jpg", "jpeg", "doc", "docx"])])
    submit = SubmitField("Envoyer le complément")
