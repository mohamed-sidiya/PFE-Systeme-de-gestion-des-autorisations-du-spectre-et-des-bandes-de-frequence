from decimal import Decimal, ROUND_HALF_UP


TAX_RATE = Decimal("19.00")
POWER_MULTIPLIERS = {
    "basse": Decimal("0.80"),
    "moyenne": Decimal("1.00"),
    "haute": Decimal("1.30"),
}


def months_between(start, end):
    if not start or not end or end < start:
        return 12
    months = (end.year - start.year) * 12 + end.month - start.month
    if end.day > start.day:
        months += 1
    return max(months, 1)


def monthly_price_for_bande(bande):
    if not bande or bande.frequence_debut is None or bande.frequence_fin is None:
        return Decimal("30000.00")

    midpoint = (Decimal(bande.frequence_debut) + Decimal(bande.frequence_fin)) / Decimal("2")
    if midpoint < Decimal("300"):
        return Decimal("25000.00")
    if midpoint < Decimal("1000"):
        return Decimal("45000.00")
    if midpoint < Decimal("3000"):
        return Decimal("80000.00")
    return Decimal("120000.00")


def quantize_money(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def build_facture_amounts(demande):
    periode_mois = months_between(demande.date_debut_souhaitee, demande.date_fin_souhaitee)
    power_multiplier = POWER_MULTIPLIERS.get(demande.puissance, Decimal("1.00"))
    prix_unitaire = quantize_money(monthly_price_for_bande(demande.bande) * power_multiplier)
    montant_ht = quantize_money(prix_unitaire * periode_mois)
    montant_taxe = quantize_money(montant_ht * TAX_RATE / Decimal("100"))
    montant_ttc = quantize_money(montant_ht + montant_taxe)
    designation = f"Redevance d'utilisation de bande - {demande.bande.designation if demande.bande else 'bande non precisee'}"
    return {
        "designation": designation,
        "periode_mois": periode_mois,
        "prix_unitaire": prix_unitaire,
        "montant_ht": montant_ht,
        "taux_taxe": TAX_RATE,
        "montant_taxe": montant_taxe,
        "montant_ttc": montant_ttc,
    }
