from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SelectField, DecimalField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class DemandeForm(FlaskForm):
    bande_id = SelectField("Bande de frequence", coerce=int, validators=[Optional()])
    objet = StringField("Descriptif du projet / expose des motifs", validators=[DataRequired(), Length(max=255)])
    type_demande = SelectField("Nature de l'utilisation", choices=[
        ("nouvelle", "Creation"),
        ("renouvellement", "Renouvellement"),
        ("modification", "Modification"),
    ])
    service_concerne = StringField("Service concerne", validators=[Optional(), Length(max=150)])
    frequence_min = DecimalField("Frequence minimale", places=3, validators=[Optional()])
    frequence_max = DecimalField("Frequence maximale", places=3, validators=[Optional()])
    unite = SelectField("Unite", choices=[("kHz", "kHz"), ("MHz", "MHz"), ("GHz", "GHz")], default="MHz")
    zone_utilisation = StringField("Zone de couverture / coordonnees", validators=[Optional(), Length(max=255)])
    puissance = SelectField("Puissance d'emission", choices=[
        ("", "Non precisee"),
        ("haute", "Haute"),
        ("moyenne", "Moyenne"),
        ("basse", "Basse"),
    ], validators=[Optional()])
    date_debut_souhaitee = DateField("Date debut souhaitee", validators=[Optional()])
    date_fin_souhaitee = DateField("Date fin souhaitee", validators=[Optional()])
    document_requis = FileField("Dossier technique et administratif (PDF)", validators=[FileRequired(), FileAllowed(["pdf"], "Seuls les fichiers PDF sont autorises.")])
    submit = SubmitField("Soumettre la demande")


class PieceForm(FlaskForm):
    type_document = StringField("Type de document", validators=[Optional(), Length(max=100)])
    fichier = FileField("Fichier", validators=[DataRequired(), FileAllowed(["pdf", "png", "jpg", "jpeg", "doc", "docx"])])
    submit = SubmitField("Ajouter")


class ComplementForm(FlaskForm):
    commentaire = TextAreaField("Reponse au complement", validators=[DataRequired()])
    fichier = FileField("Fichier complementaire", validators=[Optional(), FileAllowed(["pdf", "png", "jpg", "jpeg", "doc", "docx"])])
    submit = SubmitField("Envoyer le complement")
