from datetime import datetime, date
from sqlalchemy import event
from sqlalchemy.orm.attributes import get_history
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager
from .utils.constants import STATUT_COMPTE_ATTENTE, STATUT_COMPTE_VALIDE


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True),
)


class Permission(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    permissions = db.relationship(
        "Permission",
        secondary=role_permissions,
        backref=db.backref("roles", lazy="dynamic"),
        lazy="dynamic",
    )

    def has_permission(self, code):
        return self.permissions.filter_by(code=code).first() is not None


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    # Règle métier : le rôle est fixé à la création et ne peut pas être changé.
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    role_locked = db.Column(db.Boolean, nullable=False, default=True)

    statut_compte = db.Column(db.String(50), nullable=False, default=STATUT_COMPTE_ATTENTE)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_validation = db.Column(db.DateTime, nullable=True)

    valide_par_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    valide_par = db.relationship("User", remote_side=[id], foreign_keys=[valide_par_id])

    derniere_connexion = db.Column(db.DateTime, nullable=True)

    role = db.relationship("Role", foreign_keys=[role_id])
    profil = db.relationship(
        "ProfilUtilisateur",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        foreign_keys="ProfilUtilisateur.user_id",
    )

    demandes = db.relationship(
        "DemandeAutorisation",
        back_populates="utilisateur",
        foreign_keys="DemandeAutorisation.utilisateur_id",
        lazy=True,
    )

    observations = db.relationship("Observation", back_populates="auteur", lazy=True)
    decisions = db.relationship("Decision", back_populates="agent", lazy=True)
    historiques = db.relationship("HistoriqueAction", back_populates="utilisateur", lazy=True)

    @property
    def is_active(self):
        return self.statut_compte == STATUT_COMPTE_VALIDE

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *role_names):
        return self.role is not None and self.role.nom in role_names

    def can(self, permission_code):
        return self.role is not None and self.role.has_permission(permission_code)

    def __repr__(self):
        return f"<User {self.email}>"


@event.listens_for(User, "before_update")
def prevent_role_change(mapper, connection, target):
    history = get_history(target, "role_id")
    if target.role_locked and history.has_changes():
        raise ValueError("Le changement de rôle est interdit après la création du compte.")


class ProfilUtilisateur(db.Model):
    __tablename__ = "profils_utilisateurs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    type_utilisateur = db.Column(db.String(50), nullable=False, default="entreprise")
    raison_sociale = db.Column(db.String(255), nullable=False)
    identifiant = db.Column(db.String(100), nullable=True)
    nif_verifie = db.Column(db.Boolean, nullable=False, default=False)
    nif_verifie_par_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    date_verification_nif = db.Column(db.DateTime, nullable=True)
    telephone = db.Column(db.String(50), nullable=True)
    adresse = db.Column(db.String(255), nullable=True)
    secteur_activite = db.Column(db.String(150), nullable=True)

    user = db.relationship("User", back_populates="profil", foreign_keys=[user_id])
    nif_verifie_par = db.relationship("User", foreign_keys=[nif_verifie_par_id])

    def __repr__(self):
        return f"<ProfilUtilisateur {self.raison_sociale}>"


class BandeFrequence(db.Model):
    __tablename__ = "bandes_frequence"
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(150), nullable=False)
    frequence_debut = db.Column(db.Numeric(12, 3), nullable=False)
    frequence_fin = db.Column(db.Numeric(12, 3), nullable=False)
    unite = db.Column(db.String(20), nullable=False, default="MHz")
    usage_service = db.Column(db.String(150), nullable=True)
    statut = db.Column(db.String(50), nullable=False, default="reference")
    description = db.Column(db.Text, nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    demandes = db.relationship("DemandeAutorisation", back_populates="bande", lazy=True)
    autorisations = db.relationship("Autorisation", back_populates="bande", lazy=True)


class DemandeAutorisation(db.Model):
    __tablename__ = "demandes_autorisation"
    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False, index=True)

    utilisateur_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    bande_id = db.Column(db.Integer, db.ForeignKey("bandes_frequence.id"), nullable=True)

    objet = db.Column(db.String(255), nullable=False)
    type_demande = db.Column(db.String(100), nullable=True)
    service_concerne = db.Column(db.String(150), nullable=True)

    frequence_min = db.Column(db.Numeric(12, 3), nullable=True)
    frequence_max = db.Column(db.Numeric(12, 3), nullable=True)
    unite = db.Column(db.String(20), default="MHz")

    zone_utilisation = db.Column(db.String(255), nullable=True)
    puissance = db.Column(db.String(20), nullable=True)

    date_debut_souhaitee = db.Column(db.Date, nullable=True)
    date_fin_souhaitee = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)

    statut = db.Column(db.String(50), nullable=False, default="brouillon")
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_soumission = db.Column(db.DateTime, nullable=True)
    date_derniere_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    utilisateur = db.relationship("User", back_populates="demandes", foreign_keys=[utilisateur_id])
    bande = db.relationship("BandeFrequence", back_populates="demandes")

    pieces_jointes = db.relationship("PieceJointe", back_populates="demande", cascade="all, delete-orphan")
    observations = db.relationship("Observation", back_populates="demande", cascade="all, delete-orphan")
    decision = db.relationship("Decision", back_populates="demande", uselist=False, cascade="all, delete-orphan")
    autorisation = db.relationship("Autorisation", back_populates="demande", uselist=False, cascade="all, delete-orphan")
    facture = db.relationship("Facture", back_populates="demande", uselist=False, cascade="all, delete-orphan")
    historiques = db.relationship("HistoriqueAction", back_populates="demande", cascade="all, delete-orphan")

    def changer_statut(self, nouveau_statut):
        self.statut = nouveau_statut
        self.date_derniere_modification = datetime.utcnow()

    def peut_generer_autorisation(self):
        return self.statut == "validee" and self.decision is not None and self.autorisation is None


class PieceJointe(db.Model):
    __tablename__ = "pieces_jointes"
    id = db.Column(db.Integer, primary_key=True)
    demande_id = db.Column(db.Integer, db.ForeignKey("demandes_autorisation.id"), nullable=False)
    ajoutee_par_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    nom_original = db.Column(db.String(255), nullable=False)
    nom_stockage = db.Column(db.String(255), nullable=False)
    type_document = db.Column(db.String(100), nullable=True)
    chemin = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    taille_octets = db.Column(db.Integer, nullable=True)
    date_upload = db.Column(db.DateTime, default=datetime.utcnow)

    demande = db.relationship("DemandeAutorisation", back_populates="pieces_jointes")
    ajoutee_par = db.relationship("User", foreign_keys=[ajoutee_par_id])


class Observation(db.Model):
    __tablename__ = "observations"
    id = db.Column(db.Integer, primary_key=True)
    demande_id = db.Column(db.Integer, db.ForeignKey("demandes_autorisation.id"), nullable=False)
    auteur_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    type_observation = db.Column(db.String(50), nullable=False, default="generale")
    contenu = db.Column(db.Text, nullable=False)
    date_observation = db.Column(db.DateTime, default=datetime.utcnow)

    demande = db.relationship("DemandeAutorisation", back_populates="observations")
    auteur = db.relationship("User", back_populates="observations")


class Decision(db.Model):
    __tablename__ = "decisions"
    id = db.Column(db.Integer, primary_key=True)
    demande_id = db.Column(db.Integer, db.ForeignKey("demandes_autorisation.id"), unique=True, nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    type_decision = db.Column(db.String(50), nullable=False)
    motif = db.Column(db.Text, nullable=True)
    date_decision = db.Column(db.DateTime, default=datetime.utcnow)

    demande = db.relationship("DemandeAutorisation", back_populates="decision")
    agent = db.relationship("User", back_populates="decisions")


class Autorisation(db.Model):
    __tablename__ = "autorisations"
    id = db.Column(db.Integer, primary_key=True)
    demande_id = db.Column(db.Integer, db.ForeignKey("demandes_autorisation.id"), unique=True, nullable=False)
    bande_id = db.Column(db.Integer, db.ForeignKey("bandes_frequence.id"), nullable=True)
    creee_par_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    numero_autorisation = db.Column(db.String(100), unique=True, nullable=False, index=True)
    date_debut = db.Column(db.Date, nullable=False)
    date_fin = db.Column(db.Date, nullable=False)
    statut = db.Column(db.String(50), nullable=False, default="active")
    document_url = db.Column(db.String(255), nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    demande = db.relationship("DemandeAutorisation", back_populates="autorisation")
    bande = db.relationship("BandeFrequence", back_populates="autorisations")
    creee_par = db.relationship("User", foreign_keys=[creee_par_id])

    def est_expiree(self):
        return date.today() > self.date_fin


class Facture(db.Model):
    __tablename__ = "factures"
    id = db.Column(db.Integer, primary_key=True)
    numero_facture = db.Column(db.String(100), unique=True, nullable=False, index=True)
    demande_id = db.Column(db.Integer, db.ForeignKey("demandes_autorisation.id"), unique=True, nullable=False)
    creee_par_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    designation = db.Column(db.String(255), nullable=False)
    periode_mois = db.Column(db.Integer, nullable=False, default=1)
    prix_unitaire = db.Column(db.Numeric(12, 2), nullable=False)
    montant_ht = db.Column(db.Numeric(12, 2), nullable=False)
    taux_taxe = db.Column(db.Numeric(5, 2), nullable=False, default=19)
    montant_taxe = db.Column(db.Numeric(12, 2), nullable=False)
    montant_ttc = db.Column(db.Numeric(12, 2), nullable=False)
    statut = db.Column(db.String(50), nullable=False, default="generee")
    date_paiement = db.Column(db.DateTime, nullable=True)
    payee_par_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    demande = db.relationship("DemandeAutorisation", back_populates="facture")
    creee_par = db.relationship("User", foreign_keys=[creee_par_id])
    payee_par = db.relationship("User", foreign_keys=[payee_par_id])


class HistoriqueAction(db.Model):
    __tablename__ = "historique_actions"
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    demande_id = db.Column(db.Integer, db.ForeignKey("demandes_autorisation.id"), nullable=True)

    action = db.Column(db.String(150), nullable=False)
    entite = db.Column(db.String(100), nullable=True)
    entite_id = db.Column(db.Integer, nullable=True)
    ancien_statut = db.Column(db.String(50), nullable=True)
    nouveau_statut = db.Column(db.String(50), nullable=True)
    commentaire = db.Column(db.Text, nullable=True)
    date_action = db.Column(db.DateTime, default=datetime.utcnow)

    utilisateur = db.relationship("User", back_populates="historiques")
    demande = db.relationship("DemandeAutorisation", back_populates="historiques")


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    titre = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    lue = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_lecture = db.Column(db.DateTime, nullable=True)

    utilisateur = db.relationship("User", backref=db.backref("notifications", lazy=True))
