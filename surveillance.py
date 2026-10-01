import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin

URL = "https://jacques-maure.ecollege.haute-garonne.fr/"
FICHIER = "derniere_actualite.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def recuperer_actualites():
    r = requests.get(URL, headers=HEADERS, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    actualites = []

    # Recherche des liens de la page contenant les actualités
    for a in soup.find_all("a", href=True):
        titre = a.get_text(" ", strip=True)
        lien = urljoin(URL, a["href"])

        if not titre:
            continue

        texte = (titre + " " + lien).lower()

        if "actualit" in texte:
            actualites.append({
                "titre": titre,
                "lien": lien
            })

    # Supprime les doublons
    uniques = []
    vus = set()

    for actu in actualites:
        if actu["lien"] not in vus:
            vus.add(actu["lien"])
            uniques.append(actu)

    return uniques


def charger_derniere():
    if not os.path.exists(FICHIER):
        return None

    try:
        with open(FICHIER, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None


def sauvegarder(actu):
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump(actu, f, ensure_ascii=False, indent=2)


def envoyer_notification(actu):
    webhook = os.environ.get("DISCORD_WEBHOOK")

    if not webhook:
        print("⚠️ Aucun webhook configuré.")
        return

    message = (
        "🏫 **ACTU JACQUES MAURÉ**\n\n"
        "📢 **Nouvelle actualité publiée !**\n\n"
        f"📰 **{actu['titre']}**\n\n"
        f"🔗 {actu['lien']}"
    )

    r = requests.post(
        webhook,
        json={"content": message},
        timeout=20
    )

    r.raise_for_status()
    print("✅ Notification envoyée !")


actualites = recuperer_actualites()

if not actualites:
    print("❌ Aucune actualité trouvée.")
    exit()

# On prend la première actualité trouvée
derniere_actu = actualites[0]

ancienne = charger_derniere()

if ancienne is None:
    # Première installation : on mémorise sans envoyer de notification
    sauvegarder(derniere_actu)
    print("✅ Première installation terminée.")
    print("📌 Actualité mémorisée :", derniere_actu["titre"])

elif derniere_actu["lien"] != ancienne["lien"]:

    print("🚨 NOUVELLE ACTUALITÉ !")
    print(derniere_actu["titre"])

    envoyer_notification(derniere_actu)
    sauvegarder(derniere_actu)

else:
    print("✓ Aucune nouvelle actualité.")
