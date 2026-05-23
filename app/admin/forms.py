from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional

class AgentForm(FlaskForm):
    nom = StringField("Nom", validators=[DataRequired(), Length(max=100)])
    prenom = StringField("Prénom", validators=[Optional(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=150)])
    password = PasswordField("Mot de passe", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Créer l'agent")

class ActionCompteForm(FlaskForm):
    motif = TextAreaField("Motif / commentaire", validators=[Optional()])
    submit = SubmitField("Confirmer")
