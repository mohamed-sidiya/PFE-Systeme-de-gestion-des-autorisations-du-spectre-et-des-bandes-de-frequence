from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager


# ============================================================
# Tables d'association : User <-> Role et Role <-> Permission
# ============================================================

user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)

role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True),
)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission(db.Model):
    """Droit élémentaire, par exemple : creer_demande, valider_demande."""

    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Permission {self.code}>"


class Role(db.Model):
    """Rôle métier : Administrateur, Agent, Responsable."""

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

    def has_permission(self, permission_code):
        return self.permissions.filter_by(code=permission_code).first() is not None

    def __repr__(self):
        return f"<Role {self.nom}>"


class User(UserMixin, db.Model):
    """Utilisateur interne connecté à l'application."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    derniere_connexion = db.Column(db.DateTime, nullable=True)

    roles = db.relationship(
        "Role",
        secondary=user_roles,
        backref=db.backref("users", lazy="dynamic"),
        lazy="dynamic",
    )

    observations = db.relationship("Observation", back_populates="auteur", lazy=True)
    decisions = db.relationship("Decision", back_populates="responsable", lazy=True)
    historiques = db.relationship("HistoriqueAction", back_populates="utilisateur", lazy=True)

    @property
    def is_active(self):
        return self.actif

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return self.roles.filter_by(nom=role_name).first() is not None

    def can(self, permission_code):
        for role in self.roles.all():
            if role.has_permission(permission_code):
                return True
        return False

    def __repr__(self):
        return f"<User {self.email}>"


class Demandeur(db.Model):
    """Personne physique ou morale demandant une autorisation."""

    __tablename__ = "demandeurs"

    id = db.Column(db.Integer, primary_key=True)
    type_demandeur = db.Column(db.String(50), nullable=False)
    nom = db.Column(db.String(150), nullable=True)
    prenom = db.Column(db.String(150), nullable=True)
    raison_sociale = db.Column(db.String(255), nullable=True)
    identifiant = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    telephone = db.Column(db.String(50), nullable=True)
    adresse = db.Column(db.String(255), nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    demandes = db.relationship(
        "DemandeAutorisation",
        back_populates="demandeur",
        lazy=True,
    )

    def nom_complet(self):
        if self.raison_sociale:
            return self.raison_sociale
        return f"{self.nom or ''} {self.prenom or ''}".strip()

    def __repr__(self):
        return f"<Demandeur {self.nom_complet()}>"


class BandeFrequence(db.Model):
    """Référentiel des bandes ou plages de fréquence."""

    __tablename__ = "bandes_frequence"

    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(150), nullable=False)
    frequence_debut = db.Column(db.Numeric(12, 3), nullable=False)
    frequence_fin = db.Column(db.Numeric(12, 3), nullable=False)
    unite = db.Column(db.String(20), nullable=False, default="MHz")
    usage_service = db.Column(db.String(150), nullable=True)
    statut = db.Column(db.String(50), nullable=False, default="disponible")
    description = db.Column(db.Text, nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    demandes = db.relationship("DemandeAutorisation", back_populates="bande", lazy=True)
    autorisations = db.relationship("Autorisation", back_populates="bande", lazy=True)

    def __repr__(self):
        return f"<BandeFrequence {self.designation}>"


class DemandeAutorisation(db.Model):
    """Dossier principal de demande d'autorisation."""

    __tablename__ = "demandes_autorisation"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(100), unique=True, nullable=False, index=True)

    demandeur_id = db.Column(db.Integer, db.ForeignKey("demandeurs.id"), nullable=False)
    bande_id = db.Column(db.Integer, db.ForeignKey("bandes_frequence.id"), nullable=True)
    creee_par_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    objet = db.Column(db.String(255), nullable=False)
    type_demande = db.Column(db.String(100), nullable=True)
    service_concerne = db.Column(db.String(150), nullable=True)

    frequence_min = db.Column(db.Numeric(12, 3), nullable=True)
    frequence_max = db.Column(db.Numeric(12, 3), nullable=True)
    unite = db.Column(db.String(20), default="MHz")

    zone_utilisation = db.Column(db.String(255), nullable=True)
    puissance = db.Column(db.Numeric(10, 2), nullable=True)

    date_debut_souhaitee = db.Column(db.Date, nullable=True)
    date_fin_souhaitee = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)

    statut = db.Column(db.String(50), nullable=False, default="creee")
    dossier_complet = db.Column(db.Boolean, default=False)

    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_soumission = db.Column(db.DateTime, nullable=True)
    date_derniere_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    demandeur = db.relationship("Demandeur", back_populates="demandes")
    bande = db.relationship("BandeFrequence", back_populates="demandes")
    creee_par = db.relationship("User", foreign_keys=[creee_par_id])

    pieces_jointes = db.relationship("PieceJointe", back_populates="demande", cascade="all, delete-orphan")
    observations = db.relationship("Observation", back_populates="demande", cascade="all, delete-orphan")
    decision = db.relationship("Decision", back_populates="demande", uselist=False, cascade="all, delete-orphan")
    autorisation = db.relationship("Autorisation", back_populates="demande", uselist=False, cascade="all, delete-orphan")
    historiques = db.relationship("HistoriqueAction", back_populates="demande", cascade="all, delete-orphan")

    def changer_statut(self, nouveau_statut):
        self.statut = nouveau_statut
        self.date_derniere_modification = datetime.utcnow()

    def peut_generer_autorisation(self):
        return self.statut == "validee" and self.decision is not None

    def __repr__(self):
        return f"<DemandeAutorisation {self.reference}>"


class PieceJointe(db.Model):
    """Document numérique associé à une demande."""

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
    supprimee = db.Column(db.Boolean, default=False)
    date_suppression = db.Column(db.DateTime, nullable=True)

    demande = db.relationship("DemandeAutorisation", back_populates="pieces_jointes")
    ajoutee_par = db.relationship("User", foreign_keys=[ajoutee_par_id])

    def __repr__(self):
        return f"<PieceJointe {self.nom_original}>"


class Observation(db.Model):
    """Observation administrative, technique ou générale."""

    __tablename__ = "observations"

    id = db.Column(db.Integer, primary_key=True)
    demande_id = db.Column(db.Integer, db.ForeignKey("demandes_autorisation.id"), nullable=False)
    auteur_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type_observation = db.Column(db.String(50), nullable=False, default="generale")
    contenu = db.Column(db.Text, nullable=False)
    date_observation = db.Column(db.DateTime, default=datetime.utcnow)

    demande = db.relationship("DemandeAutorisation", back_populates="observations")
    auteur = db.relationship("User", back_populates="observations")

    def __repr__(self):
        return f"<Observation {self.type_observation}>"


class Decision(db.Model):
    """Décision finale du responsable : validation ou rejet."""

    __tablename__ = "decisions"

    id = db.Column(db.Integer, primary_key=True)
    demande_id = db.Column(db.Integer, db.ForeignKey("demandes_autorisation.id"), unique=True, nullable=False)
    responsable_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type_decision = db.Column(db.String(50), nullable=False)
    motif = db.Column(db.Text, nullable=True)
    date_decision = db.Column(db.DateTime, default=datetime.utcnow)

    demande = db.relationship("DemandeAutorisation", back_populates="decision")
    responsable = db.relationship("User", back_populates="decisions")

    def __repr__(self):
        return f"<Decision {self.type_decision}>"


class Autorisation(db.Model):
    """Autorisation générée après validation d'une demande."""

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
    date_derniere_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    demande = db.relationship("DemandeAutorisation", back_populates="autorisation")
    bande = db.relationship("BandeFrequence", back_populates="autorisations")
    creee_par = db.relationship("User", foreign_keys=[creee_par_id])

    def est_active(self):
        today = date.today()
        return self.statut == "active" and self.date_debut <= today <= self.date_fin

    def est_expiree(self):
        return date.today() > self.date_fin

    def __repr__(self):
        return f"<Autorisation {self.numero_autorisation}>"


class HistoriqueAction(db.Model):
    """Journalisation des actions importantes."""

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

    def __repr__(self):
        return f"<HistoriqueAction {self.action}>"


class Notification(db.Model):
    """Notification interne destinée à un utilisateur."""

    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    titre = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    lue = db.Column(db.Boolean, default=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_lecture = db.Column(db.DateTime, nullable=True)

    utilisateur = db.relationship("User", backref=db.backref("notifications", lazy=True))

    def marquer_comme_lue(self):
        self.lue = True
        self.date_lecture = datetime.utcnow()

    def __repr__(self):
        return f"<Notification {self.titre}>"
