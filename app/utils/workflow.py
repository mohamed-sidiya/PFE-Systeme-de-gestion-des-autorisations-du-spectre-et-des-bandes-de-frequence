STATUTS_DEMANDE = {
    "brouillon": "Brouillon",
    "soumise": "Soumise",
    "en_traitement": "En traitement",
    "complement_demande": "Complément demandé",
    "completee": "Complétée",
    "validee": "Validée",
    "rejetee": "Rejetée",
    "autorisation_generee": "Autorisation générée",
    "expiree": "Expirée",
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

def transition_autorisee(statut_actuel, nouveau_statut):
    return nouveau_statut in TRANSITIONS_STATUTS_DEMANDE.get(statut_actuel, [])
