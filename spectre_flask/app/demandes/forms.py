from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, SelectField, SubmitField,
    DecimalField, DateField
)
from wtforms.validators import DataRequired, Optional, Email, Length


class DemandeurForm(FlaskForm):
    type_demandeur = SelectField("Type de demandeur", choices=[
        ("personne_physique", "Personne physique"),
        ("entreprise", "Entreprise"),
        ("organisme_public", "Organisme public"),
        ("association", "Association"),
    ])
    nom = StringField("Nom", validators=[Optional(), Length(max=150)])
    prenom = StringField("Prénom", validators=[Optional(), Length(max=150)])
    raison_sociale = StringField("Raison sociale", validators=[Optional(), Length(max=255)])
    identifiant = StringField("Identifiant", validators=[Optional(), Length(max=100)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=150)])
    telephone = StringField("Téléphone", validators=[Optional(), Length(max=50)])
    adresse = StringField("Adresse", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Enregistrer")


class DemandeForm(FlaskForm):
    demandeur_id = SelectField("Demandeur", coerce=int, validators=[DataRequired()])
    bande_id = SelectField("Bande de fréquence", coerce=int, validators=[Optional()])
    objet = StringField("Objet de la demande", validators=[DataRequired(), Length(max=255)])
    type_demande = SelectField("Type de demande", choices=[
        ("nouvelle", "Nouvelle demande"),
        ("renouvellement", "Renouvellement"),
        ("modification", "Modification"),
        ("annulation", "Annulation"),
    ])
    service_concerne = StringField("Service concerné", validators=[Optional(), Length(max=150)])
    frequence_min = DecimalField("Fréquence min", places=3, validators=[Optional()])
    frequence_max = DecimalField("Fréquence max", places=3, validators=[Optional()])
    unite = SelectField("Unité", choices=[("Hz", "Hz"), ("kHz", "kHz"), ("MHz", "MHz"), ("GHz", "GHz")], default="MHz")
    zone_utilisation = StringField("Zone d'utilisation", validators=[Optional(), Length(max=255)])
    puissance = DecimalField("Puissance", places=2, validators=[Optional()])
    date_debut_souhaitee = DateField("Date début souhaitée", validators=[Optional()])
    date_fin_souhaitee = DateField("Date fin souhaitée", validators=[Optional()])
    description = TextAreaField("Description", validators=[Optional()])
    submit = SubmitField("Enregistrer")


class PieceJointeForm(FlaskForm):
    type_document = StringField("Type de document", validators=[Optional(), Length(max=100)])
    fichier = FileField("Fichier", validators=[DataRequired(), FileAllowed(["pdf", "png", "jpg", "jpeg", "doc", "docx"], "Format non autorisé")])
    submit = SubmitField("Ajouter")


class ObservationForm(FlaskForm):
    type_observation = SelectField("Type", choices=[
        ("generale", "Générale"),
        ("administrative", "Administrative"),
        ("technique", "Technique"),
    ])
    contenu = TextAreaField("Observation", validators=[DataRequired()])
    submit = SubmitField("Ajouter l'observation")


class StatutForm(FlaskForm):
    nouveau_statut = SelectField("Nouveau statut")
    commentaire = TextAreaField("Commentaire", validators=[Optional()])
    submit = SubmitField("Changer le statut")
