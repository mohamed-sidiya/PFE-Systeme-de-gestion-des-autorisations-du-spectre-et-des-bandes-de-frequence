from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length


class UserForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(max=100)])
    prenom = StringField("Prénom", validators=[Optional(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField("Mot de passe", validators=[Optional(), Length(min=6)])
    actif = BooleanField("Compte actif", default=True)
    roles = SelectMultipleField("Rôles", coerce=int)
    submit = SubmitField("Enregistrer")


class RoleForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(max=100)])
    description = StringField("Description", validators=[Optional(), Length(max=255)])
    permissions = SelectMultipleField("Permissions", coerce=int)
    submit = SubmitField("Enregistrer")
