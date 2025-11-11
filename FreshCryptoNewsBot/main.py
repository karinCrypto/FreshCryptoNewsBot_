# ===========================================
# 🔥 FreshCryptoNews_V3.3 (Cloud Run Version)
# Title + Link 기반 AI News Brief Generator
# Curated by 엔지니어 카린 🌸
# ===========================================

from flask import Flask, request
import requests, feedparser, time, os
from datetime import datetime, timedelta
from openai import OpenAI

# =========================
# 🔑 기본 설정
# =========================
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL = "@FreshKarinsCryptonomy"

client = OpenAI(api_key=OPENAI_API_KEY)

# =========================
# 📰 무료 접근 가능한 글로벌 피드
# =========================
RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://blockchain.news/feed",
    "https://www.ccn.com/news/crypto-news/feeds/",
    "https://www.tokenpost.kr/rss"  # 🇰🇷 한국
]

# =========================
# 📰 기사 수집
# =========================
def fetch_latest_articles(limit=2):
    articles = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:limit]:
            title = entry.title
            link = entry.link
            articles.append((title, link))
    return articles[:8]

# =========================
# 🧠 AI 요약 (본문 접근 없이 추론)
# =========================
def summarize_article(title, link):
    try:
        prompt = f"""
        다음 암호화폐 뉴스 제목을 기반으로,
        뉴스 본문을 읽지 않고도 자연스럽게 이어지는
        한글 4~5줄 + 영어 4~5줄의 요약문을 작성해줘.
        시장의 흐름, 투자자 심리, 의미까지 함께 다뤄줘.
        제목: {title}
        링크: {link}
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("⚠️ 요약 실패:", e)
        return "요약을 불러오지 못했습니다."

# =========================
# 💌 메시지 생성
# =========================
def build_message():
    now_kst = datetime.utcnow() + timedelta(hours=9)
    kst_time = now_kst.strftime("%Y-%m-%d %H:%M KST")
    utc_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    articles = fetch_latest_articles()

    header = f"""
🔥 <b>FreshCryptoNews_V3.3</b>  
💨 신선한 속도로 전하는 글로벌 & 한국 크립토 브리핑  
🌸 Curated by 엔지니어 카린  
⏰ {kst_time} | 🌐 {utc_time}\n
"""

    body = ""
    for i, (title, link) in enumerate(articles, 1):
        summary = summarize_article(title, link)
        body += f"<b>{i}. {title}</b>\n{summary}\n🔗 <a href='{link}'>원문 보기</a>\n\n"

    footer = """
👩‍💻 <b>by 엔지니어 카린 (Engineer Karin)</b>  
신뢰는 느림이 아닌, 신선함과 빠름에서 온다.  
Speed with soul. Built with empathy. ⚡
"""

    return header + body + footer

# =========================
# 📡 텔레그램 발송
# =========================
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    r = requests.post(url, data=payload)
    print("📤 Sent:", r.status_code)
    return r.status_code

# =========================
# 🌐 Flask 서버 (Cloud Run 엔드포인트)
# =========================
app = Flask(__name__)

@app.route("/")
def home():
    return {"status": "FreshCryptoNews active 🚀"}, 200

@app.route("/send_news", methods=["GET"])
def send_news():
    message = build_message()
    send_message(message)
    return {"result": "✅ News sent successfully!"}, 200

# =========================
# 🚀 실행 (Cloud Run Entry Point)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
