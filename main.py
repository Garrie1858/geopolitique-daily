import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google.generativeai as genai

NEWS_API_KEY = os.environ["NEWS_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_FROM = "Julien.fameree04@gmail.com"
EMAIL_TO = "Julien.fameree04@gmail.com"

def get_news():
    regions = ["Europe", "Middle East", "China", "Russia Ukraine", "Africa", "Americas"]
    articles = []
    for region in regions:
        url = f"https://newsapi.org/v2/everything?q={region}+geopolitics&language=fr&sortBy=publishedAt&pageSize=2&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if data.get("articles"):
            for article in data["articles"]:
                articles.append(f"- {article['title']}")
    return "\n".join(articles)

def generate_summary(news_text):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-8b")
    prompt = f"""Tu es un expert en géopolitique. Voici les titres d'actualité du jour :

{news_text}

Fais un résumé géopolitique quotidien en français, structuré par région (Europe, Moyen-Orient, Asie/Chine, Russie/Ukraine, Afrique, Amériques). 
Pour chaque région, explique en 3-4 phrases les événements importants et leur contexte.
Termine par une section "À surveiller" avec 2-3 points clés pour les prochains jours."""
    response = model.generate_content(prompt)
    return response.text

def send_email(summary):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🌍 Résumé Géopolitique du Jour"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    part = MIMEText(summary, "plain")
    msg.attach(part)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

if __name__ == "__main__":
    print("Récupération des actualités...")
    news = get_news()
    print("Génération du résumé...")
    summary = generate_summary(news)
    print("Envoi de l'email...")
    send_email(summary)
    print("Email envoyé avec succès !")
