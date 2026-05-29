STATUTS_DEMANDE = {
    "brouillon": "Brouillon",
    "soumise": "Soumise",
    "en_traitement": "En traitement",
    "complement_demande": "Complement demande",
    "completee": "Completee",
    "validee": "Validee",
    "rejetee": "Rejetee",
    "autorisation_generee": "Autorisation generee",
    "expiree": "Expiree",
}

STATUT_BADGES_DEMANDE = {
    "brouillon": "secondary",
    "soumise": "info",
    "en_traitement": "primary",
    "complement_demande": "warning",
    "completee": "info",
    "validee": "success",
    "rejetee": "danger",
    "autorisation_generee": "success",
    "expiree": "secondary",
}

TRANSITIONS_STATUTS_DEMANDE = {
    "brouillon": ["soumise"],
    "soumise": ["en_traitement"],
    "en_traitement": ["complement_demande", "validee", "rejetee"],
    "complement_demande": ["completee"],
    "completee": ["en_traitement"],
    "validee": ["autorisation_generee"],
    "autorisation_generee": ["expiree"],
    "rejetee": [],
    "expiree": [],
}


def statut_label(statut):
    return STATUTS_DEMANDE.get(statut, statut)


def statut_badge(statut):
    return STATUT_BADGES_DEMANDE.get(statut, "secondary")


def transition_autorisee(statut_actuel, nouveau_statut):
    return nouveau_statut in TRANSITIONS_STATUTS_DEMANDE.get(statut_actuel, [])
