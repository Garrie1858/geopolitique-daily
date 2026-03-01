import os
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from google import genai

# ── Config ──────────────────────────────────────────
NEWS_API_KEY   = os.environ["NEWS_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
EMAIL_SENDER   = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO       = os.environ["EMAIL_USER"]

client = genai.Client(api_key=GEMINI_API_KEY)

# ── Régions à couvrir ────────────────────────────────
REGIONS = {
    "Europe":           "europe politics OR war OR crisis",
    "Moyen-Orient":     "middle east conflict OR diplomacy OR war",
    "Russie / Ukraine": "russia ukraine war",
    "Chine / Asie":     "china asia geopolitics OR taiwan OR korea",
    "Afrique":          "africa politics OR conflict OR crisis",
    "Amériques":        "usa OR latin america politics OR trump",
}

def get_news():
    all_articles = []
    for region, query in REGIONS.items():
        url = "https://newsapi.org/v2/everything"
        params = {
            "q":        query,
            "language": "fr",
            "pageSize": 2,
            "sortBy":   "publishedAt",
            "apiKey":   NEWS_API_KEY,
        }
        resp = requests.get(url, params=params, timeout=10)
        articles = resp.json().get("articles", [])
        for a in articles:
            all_articles.append({
                "region": region,
                "title":  a.get("title", ""),
                "source": a.get("source", {}).get("name", ""),
            })
    return all_articles

def generate_summary(articles):
    lines = "\n".join([f"[{a['region']}] {a['title']}" for a in articles if a['title']])
    today = datetime.now().strftime("%A %d %B %Y")
    prompt = f"""Tu es un analyste géopolitique. Voici des titres d'actualité du {today}.

{lines}

Rédige un résumé géopolitique mondial structuré par région, en français, en 8 à 10 phrases claires et concises. 
Pour chaque région mentionnée, donne les points essentiels. Commence directement sans introduction générale."""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt,
    )
    return response.text.strip()

def build_html(summary):
    today = datetime.now().strftime("%A %d %B %Y")
    paragraphs = "".join([
        f"<p style='margin:0 0 12px 0;line-height:1.7;font-size:15px;color:#1a1a1a'>{p.strip()}</p>"
        for p in summary.split("\n") if p.strip()
    ])
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f0eb;font-family:Georgia,serif">
  <div style="max-width:640px;margin:30px auto;background:#fff;border-radius:6px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08)">
    <div style="background:#1a1a1a;padding:24px 28px">
      <div style="font-size:11px;text-transform:uppercase;letter-spacing:2px;color:#d4471a;margin-bottom:6px">Résumé Géopolitique</div>
      <div style="font-size:22px;color:#fff;font-style:italic">{today}</div>
    </div>
    <div style="padding:24px 28px">
      {paragraphs}
    </div>
    <div style="padding:14px 28px;background:#f8f5f0;font-size:11px;color:#aaa;text-align:center;border-top:1px solid #eee">
      Généré automatiquement chaque matin · Sources : NewsAPI + Gemini
    </div>
  </div>
</body>
</html>"""

def send_email(subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_TO, msg.as_string())
    print("Email géopolitique envoyé !")

def main():
    print("Récupération des actualités...")
    articles = get_news()
    print(f"{len(articles)} articles récupérés")

    print("Génération du résumé...")
    summary = generate_summary(articles)
    print("Résumé généré")

    html  = build_html(summary)
    today = datetime.now().strftime("%d/%m/%Y")
    send_email(f"🌍 Géopolitique — {today}", html)

if __name__ == "__main__":
    main()
