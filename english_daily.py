import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import google.generativeai as genai

# ── Config ──────────────────────────────────────────
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
EMAIL_SENDER   = os.environ["EMAIL_USER"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO       = os.environ["EMAIL_USER"]

genai.configure(api_key=GEMINI_API_KEY)

# ── Thèmes du cours + vie quotidienne ───────────────
TOPICS = [
    "a job interview for a construction project manager position",
    "a first day at work on a construction site",
    "a professional email about a delayed building permit",
    "a meeting between an architect and a contractor about a project tender",
    "visiting a skyscraper under construction in Dubai",
    "explaining 3D-printed homes to a client",
    "a conversation about sustainable construction methods",
    "describing your personal qualities during a job interview",
    "a site inspection after heavy rain caused damage",
    "negotiating a contract with a subcontractor",
    "presenting a construction project to stakeholders",
    "asking for directions in a foreign city",
    "ordering food at a restaurant abroad",
    "checking into a hotel and asking for local tips",
    "small talk with a foreign colleague about the weekend",
    "a phone call to reschedule a meeting",
    "discussing the metaverse and digital twins in construction",
    "a conversation about work-life balance with a colleague",
    "explaining your company culture during an interview",
    "describing a megastructure like the Millau Viaduct to a friend",
]

# ── Vocabulaire clé à intégrer ───────────────────────
VOCAB_POOLS = [
    ["reliable", "deadline", "stakeholder", "compliance", "tender"],
    ["scaffold", "reinforced concrete", "load-bearing", "permit", "blueprint"],
    ["proactive", "articulate", "self-disciplined", "resourceful", "dedicated"],
    ["sustainable", "digital twin", "earthworks", "milestone", "subcontractor"],
    ["procurement", "liability", "estimate", "feasible", "leverage"],
    ["furthermore", "nevertheless", "hence", "acknowledge", "outcomes"],
    ["viaduct", "masonry", "buttress", "curvature", "exoskeleton"],
    ["fringe benefits", "redundancy", "commission", "forthcoming", "concise"],
    ["collaborate", "innovative", "momentum", "adjacent", "allocate"],
    ["fit-out", "cladding", "snagging", "commissioning", "retaining wall"],
]

def build_prompt(topic, vocab_words):
    today = datetime.now().strftime("%A %d %B %Y")
    words_str = ", ".join(vocab_words)
    return f"""
You are an English teacher creating a daily bilingual reading exercise for a French-speaking Belgian engineering student (level A2-B1) studying construction.

Today is {today}.
Topic: {topic}
Vocabulary to include (use at least 4 of these naturally): {words_str}

Write a text of exactly 12 sentences following this strict format:
- Alternate EVERY sentence: one sentence in FRENCH, then the same sentence in ENGLISH
- So: French sentence 1, English sentence 1, French sentence 2, English sentence 2... etc.
- Each sentence pair must convey the exact same meaning
- The text must tell a coherent short story or scene related to the topic
- Vocabulary level: B1, accessible but educational
- Bold the vocabulary words from the list when they appear in the English sentences

Format your response EXACTLY like this, with no extra text, titles or commentary:

FR: [French sentence 1]
EN: [English sentence 1]

FR: [French sentence 2]
EN: [English sentence 2]

(continue for all 12 sentences)
"""

def generate_text(topic, vocab_words):
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    prompt = build_prompt(topic, vocab_words)
    response = model.generate_content(prompt)
    return response.text.strip()

def parse_pairs(raw_text):
    """Parse FR/EN pairs from Gemini output."""
    pairs = []
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    i = 0
    while i < len(lines):
        fr_line = en_line = ""
        if lines[i].startswith("FR:"):
            fr_line = lines[i][3:].strip()
            i += 1
        if i < len(lines) and lines[i].startswith("EN:"):
            en_line = lines[i][3:].strip()
            i += 1
        if fr_line or en_line:
            pairs.append((fr_line, en_line))
    return pairs

def build_html_email(topic, pairs, vocab_words):
    today = datetime.now().strftime("%A %d %B %Y")
    vocab_str = " · ".join([f"<span style='background:#fff3cd;padding:1px 5px;border-radius:3px'>{w}</span>" for w in vocab_words])

    rows_html = ""
    for i, (fr, en) in enumerate(pairs, 1):
        bg = "#fafafa" if i % 2 == 0 else "#ffffff"
        rows_html += f"""
        <tr style="background:{bg}">
          <td style="padding:10px 14px;font-size:14px;color:#555;border-right:1px solid #eee;width:50%;vertical-align:top">
            🇫🇷 {fr}
          </td>
          <td style="padding:10px 14px;font-size:14px;color:#1a1a1a;width:50%;vertical-align:top">
            🇬🇧 {en}
          </td>
        </tr>"""

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f0eb;font-family:'Georgia',serif">
  <div style="max-width:680px;margin:30px auto;background:#ffffff;border-radius:6px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08)">

    <!-- Header -->
    <div style="background:#1a1a1a;padding:24px 28px">
      <div style="font-size:11px;text-transform:uppercase;letter-spacing:2px;color:#d4471a;margin-bottom:6px">English Daily</div>
      <div style="font-size:22px;color:#ffffff;font-style:italic">{today}</div>
      <div style="font-size:13px;color:#aaa;margin-top:4px">📖 {topic.capitalize()}</div>
    </div>

    <!-- Vocab highlight -->
    <div style="background:#fffbf0;border-bottom:1px solid #f0e4c0;padding:12px 28px;font-size:12px;color:#7a6030">
      💡 Vocabulaire du jour : {vocab_str}
    </div>

    <!-- Bilingual table -->
    <table style="width:100%;border-collapse:collapse;border-top:1px solid #eee">
      <thead>
        <tr style="background:#f8f5f0">
          <th style="padding:8px 14px;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#999;text-align:left;border-right:1px solid #eee">Français</th>
          <th style="padding:8px 14px;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#999;text-align:left">English</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>

    <!-- Footer -->
    <div style="padding:18px 28px;background:#f8f5f0;font-size:11px;color:#aaa;text-align:center;border-top:1px solid #eee">
      English Daily · Généré automatiquement chaque matin à 8h00 🇧🇪
    </div>
  </div>
</body>
</html>"""
    return html

def send_email(subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_TO, msg.as_string())
    print("Email sent successfully!")

def main():
    topic      = random.choice(TOPICS)
    vocab_words = random.choice(VOCAB_POOLS)

    print(f"Topic: {topic}")
    print(f"Vocab: {vocab_words}")

    raw = generate_text(topic, vocab_words)
    print("--- RAW OUTPUT ---")
    print(raw)

    pairs = parse_pairs(raw)
    print(f"Parsed {len(pairs)} sentence pairs")

    html  = build_html_email(topic, pairs, vocab_words)
    today = datetime.now().strftime("%d/%m/%Y")
    send_email(f"🇬🇧 English Daily — {today}", html)

if __name__ == "__main__":
    main()
