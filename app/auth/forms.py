from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(max=150)])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    remember = BooleanField("Se souvenir de moi")
    submit = SubmitField("Se connecter")

class RegisterForm(FlaskForm):
    nom = StringField("Nom du représentant", validators=[DataRequired(), Length(max=100)])
    prenom = StringField("Prénom", validators=[Optional(), Length(max=100)])
    email = StringField("Email professionnel", validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirmer le mot de passe", validators=[DataRequired(), EqualTo("password")])
    type_utilisateur = SelectField("Type", choices=[
        ("entreprise", "Entreprise"),
        ("organisme", "Organisme"),
        ("administration", "Administration"),
    ])
    raison_sociale = StringField("Raison sociale", validators=[DataRequired(), Length(max=255)])
    identifiant = StringField("Identifiant / NIF / RC", validators=[Optional(), Length(max=100)])
    telephone = StringField("Téléphone", validators=[Optional(), Length(max=50)])
    adresse = StringField("Adresse", validators=[Optional(), Length(max=255)])
    secteur_activite = StringField("Secteur d'activité", validators=[Optional(), Length(max=150)])
    submit = SubmitField("Créer le compte")
