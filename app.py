import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# --- الإعدادات ---
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRWcL2mYT3X4Hw8EqPPvu0s73h7cJ4LGYFsgarwZCV5MyRMbAqA1xmlpZB1HdRw7ZBWVgLCa3jpdC03wavmmVQhKERygzgAhRZCyssibLFntq5qpRroYjMObVoZC9SsYlq93jPZAmxYKabu0wctd9Lr8MvjEdOZB7fvVwtlbk71XFknmJGVHI7kYLYBxEYCWwDhPKU0jrnDN"
VERIFY_TOKEN = "Gypsum_2026_Secret"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_INSTRUCTIONS = """
أنت 'جورج'، خبير جبس بورد مصري محترف وصاحب شركة 'تقنيات الجبس بورد'.
رد بلهجة مصرية ودودة وشاطرة. 
مميزاتنا: ميزان ليزر، صاج محمل 0.4 و 0.5، خامات كناوف.
لو سأل عن السعر: السعر حسب التصميم، اطلب منه يبعت صورة أو يحدد موعد معاينة مجانية.
"""

@app.route("/", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "failed", 403

@app.route("/", methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data["entry"]:
            for msg in entry.get("messaging", []):
                if msg.get("message") and not msg["message"].get("is_echo"):
                    sender_id = msg["sender"]["id"]
                    user_text = msg["message"].get("text")
                    if user_text:
                        # طلب الرد من Groq (بديل Gemini العالمي)
                        chat_completion = client.chat.completions.create(
                            messages=[
                                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                                {"role": "user", "content": user_text}
                            ],
                            model="llama3-8b-8192",
                        )
                        ai_answer = chat_completion.choices[0].message.content
                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def send_fb_message(pid, txt):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": pid}, "message": {"text": txt}})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
