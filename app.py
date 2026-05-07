import os
import requests
import sys
from flask import Flask, request
from groq import Groq

# إجبار السيرفر على التعامل مع اللغة العربية (UTF-8)
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)

# --- الإعدادات ---
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRTLUS3KD5yKTxzamQjJQBNNZArXGiZByKPgVyP7g7AKO7qjuYUZAzbLFBDZBLZByfmdUryaZCFz7s3O9Wr91Uwzn0Rgq3u5StAByiXhiTYeznKZBr0doQvO8JXv271nnWiZApKkSPZBOBoZCs1zvSbc2pxxoOTNNEZBn1A75xsXsp8kRmlmm478OqEKlbaghTJ9ZBnYPdxNX2ywd"
VERIFY_TOKEN = "Gypsum_2026_Secret"
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

# التعليمات بالعربية والإنجليزية لضمان عدم حدوث Error
SYSTEM_INSTRUCTIONS = "You are George, an Egyptian gypsum board expert. Reply only in Egyptian Arabic. Talk about laser levels, Knauf materials, and thick metal (0.4/0.5). If asked about price, ask for a design photo and location for a free estimate."

@app.route("/", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403

@app.route("/", methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data["entry"]:
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message") and not messaging_event["message"].get("is_echo"):
                    sender_id = messaging_event["sender"]["id"]
                    user_text = messaging_event["message"].get("text", "")
                    
                    if user_text:
                        try:
                            # طلب الرد من Groq
                            completion = client.chat.completions.create(
                                model="llama3-8b-8192",
                                messages=[
                                    {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                                    {"role": "user", "content": user_text}
                                ]
                            )
                            ai_answer = completion.choices[0].message.content
                        except Exception as e:
                            # طباعة الخطأ بشكل سليم
                            print(f"DEBUG ERROR: {str(e)}")
                            ai_answer = "يا فنان نورتنا! المهندس جورج معاك، قولي محتاج تعمل جبس بورد فين بالظبط؟"
                        
                        send_fb_message(sender_id, ai_answer)
                        
    return "ok", 200

def send_fb_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    # إرسال النص بترميز JSON سليم ليدعم العربية
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
