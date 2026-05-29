from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def money(value):
    return f"{value:.2f} MRU"


def build_facture_pdf(facture):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Republique Islamique de Mauritanie", styles["Title"]))
    story.append(Paragraph("Autorite de Regulation des Telecommunications", styles["Heading2"]))
    story.append(Paragraph("Facture - Redevance d'utilisation de frequences", styles["Heading3"]))
    story.append(Spacer(1, 0.5 * cm))

    demande = facture.demande
    profil = demande.utilisateur.profil
    client_name = profil.raison_sociale if profil else demande.utilisateur.email
    client_address = profil.adresse if profil and profil.adresse else "-"
    client_identifiant = profil.identifiant if profil and profil.identifiant else "-"

    meta = [
        ["Numero facture", facture.numero_facture, "Date", facture.date_creation.strftime("%d/%m/%Y") if facture.date_creation else "-"],
        ["Reference demande", demande.reference, "Statut", facture.statut],
        ["Redevable", client_name, "NIF / Identifiant", client_identifiant],
        ["Adresse", client_address, "Email", demande.utilisateur.email],
    ]
    meta_table = Table(meta, colWidths=[3.5 * cm, 6 * cm, 3.5 * cm, 5 * cm])
    meta_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("BACKGROUND", (2, 0), (2, -1), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.6 * cm))

    items = [
        ["Designation", "Periode", "Prix mensuel HT", "Montant HT"],
        [facture.designation, f"{facture.periode_mois} mois", money(facture.prix_unitaire), money(facture.montant_ht)],
    ]
    items_table = Table(items, colWidths=[8 * cm, 3 * cm, 3.5 * cm, 3.5 * cm])
    items_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 0.5 * cm))

    totals = [
        ["Montant HT", money(facture.montant_ht)],
        [f"TVA {facture.taux_taxe:.2f}%", money(facture.montant_taxe)],
        ["Total TTC", money(facture.montant_ttc)],
    ]
    totals_table = Table(totals, colWidths=[5 * cm, 4 * cm], hAlign="RIGHT")
    totals_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightblue),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 0.6 * cm))

    if facture.date_paiement:
        story.append(Paragraph(f"Paiement enregistre le {facture.date_paiement.strftime('%d/%m/%Y %H:%M')}.", styles["Normal"]))
    else:
        story.append(Paragraph("Facture en attente de paiement.", styles["Normal"]))

    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph("Cachet / Signature", styles["Heading3"]))

    doc.build(story)
    buffer.seek(0)
    return buffer


def build_autorisation_pdf(autorisation):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
    )
    styles = getSampleStyleSheet()
    story = []

    demande = autorisation.demande
    facture = demande.facture
    profil = demande.utilisateur.profil
    client_name = profil.raison_sociale if profil else demande.utilisateur.email
    client_address = profil.adresse if profil and profil.adresse else "-"
    client_identifiant = profil.identifiant if profil and profil.identifiant else "-"

    story.append(Paragraph("Republique Islamique de Mauritanie", styles["Title"]))
    story.append(Paragraph("Autorite de Regulation des Telecommunications", styles["Heading2"]))
    story.append(Paragraph("Autorisation d'utilisation de bandes de frequences", styles["Heading3"]))
    story.append(Paragraph("Quittance de paiement associee", styles["Heading3"]))
    story.append(Spacer(1, 0.5 * cm))

    meta = [
        ["Numero autorisation", autorisation.numero_autorisation, "Date emission", autorisation.date_creation.strftime("%d/%m/%Y") if autorisation.date_creation else "-"],
        ["Reference demande", demande.reference, "Statut", autorisation.statut],
        ["Facture", facture.numero_facture if facture else "-", "Montant acquitte", money(facture.montant_ttc) if facture else "-"],
        ["Date paiement", facture.date_paiement.strftime("%d/%m/%Y %H:%M") if facture and facture.date_paiement else "-", "Agent", autorisation.creee_par.email if autorisation.creee_par else "-"],
    ]
    meta_table = Table(meta, colWidths=[3.8 * cm, 5.7 * cm, 3.8 * cm, 4.7 * cm])
    meta_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("BACKGROUND", (2, 0), (2, -1), colors.whitesmoke),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * cm))

    beneficiary = [
        ["Beneficiaire", client_name],
        ["NIF / Identifiant", client_identifiant],
        ["Adresse", client_address],
        ["Email", demande.utilisateur.email],
    ]
    beneficiary_table = Table(beneficiary, colWidths=[4 * cm, 14 * cm])
    beneficiary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(beneficiary_table)
    story.append(Spacer(1, 0.5 * cm))

    technical = [
        ["Bande", autorisation.bande.designation if autorisation.bande else "-"],
        ["Frequences", f"{demande.frequence_min or '-'} - {demande.frequence_max or '-'} {demande.unite}"],
        ["Puissance", demande.puissance or "-"],
        ["Zone de couverture", demande.zone_utilisation or "-"],
        ["Validite", f"Du {autorisation.date_debut.strftime('%d/%m/%Y') if autorisation.date_debut else '-'} au {autorisation.date_fin.strftime('%d/%m/%Y') if autorisation.date_fin else '-'}"],
    ]
    technical_table = Table(technical, colWidths=[4 * cm, 14 * cm])
    technical_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(Paragraph("Caracteristiques autorisees", styles["Heading3"]))
    story.append(technical_table)
    story.append(Spacer(1, 0.6 * cm))

    story.append(Paragraph(
        "La presente autorisation est delivree apres instruction de la demande et paiement de la redevance correspondante. "
        "Elle vaut quittance pour le montant indique ci-dessus.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 1.2 * cm))

    signature = Table(
        [["Cachet de l'autorite", "Signature de l'agent habilite"], ["", autorisation.creee_par.email if autorisation.creee_par else "-"]],
        colWidths=[9 * cm, 9 * cm],
    )
    signature.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING", (0, 1), (-1, 1), 40),
    ]))
    story.append(signature)

    doc.build(story)
    buffer.seek(0)
    return buffer
