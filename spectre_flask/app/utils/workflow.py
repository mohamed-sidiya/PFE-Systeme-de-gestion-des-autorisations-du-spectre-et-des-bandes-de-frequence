STATUTS_DEMANDE = {
    "creee": "Créée",
    "en_verification": "En vérification",
    "complement_demande": "Complément demandé",
    "prete_decision": "Prête à décision",
    "validee": "Validée",
    "rejetee": "Rejetée",
    "autorisation_generee": "Autorisation générée",
    "expiree": "Expirée",
}

TRANSITIONS_STATUTS_DEMANDE = {
    "creee": ["en_verification"],
    "en_verification": ["complement_demande", "prete_decision"],
    "complement_demande": ["en_verification"],
    "prete_decision": [],
    "validee": [],
    "autorisation_generee": ["expiree"],
    "rejetee": [],
    "expiree": [],
}


def transition_autorisee(statut_actuel, nouveau_statut):
    return nouveau_statut in TRANSITIONS_STATUTS_DEMANDE.get(statut_actuel, [])


def statuts_suivants(statut_actuel):
    return TRANSITIONS_STATUTS_DEMANDE.get(statut_actuel, [])
