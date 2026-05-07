import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# --- الإعدادات (تأكد من دقتها) ---
# التوكن الخاص بفيسبوك (موجود في إعدادات التطبيق)
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRWqPsd35SgrWib0ssEzJhWrNHvAdGhfmZB098NfkbQvQeVTPZCjh3CvSVAkG0GbS5iKP2CGjg5dBHY7P4zIyga67Jsk9nILlmR9OtZBpUuN3YRxhATBUuj1ZCCnkgAtxZBtAM3JYkUJZAsEeu1Bbbr9hihGvhrGXd8hps2bF0hsjWHx7UePIkUirpHSBTvMcKFnUFcZCaYl"
# توكن التحقق (الذي وضعته في Webhook فيسبوك)
VERIFY_TOKEN = "Gypsum_2026_Secret"
# مفتاح Groq (تأكد إنه شغال وجديد)
GROQ_API_KEY = "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"

# تهيئة عميل Groq
client = Groq(api_key=GROQ_API_KEY)

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
                    user_text = messaging_event["message"].get("text")
                    
                    if user_text:
                        try:
                            # طلب الرد من موديل Llama 3 الصاروخي
                            completion = client.chat.completions.create(
                                model="llama3-8b-8192",
                                messages=[
                                    {"role": "system", "content": "أنت 'جورج'، فنان جبس بورد مصري. رد بلهجة مصرية عامية. اتكلم عن دقة ميزان الليزر، وخامات كناوف، وصاج محمل. لو سأل عن السعر قوله يبعت صورة للتصميم والمساحة عشان نحدد موعد معاينة مجانية."},
                                    {"role": "user", "content": user_text}
                                ]
                            )
                            response_text = completion.choices[0].message.content
                        except Exception as e:
                            # طباعة الخطأ في Railway Logs لمعرفته
                            print(f"Error calling Groq: {e}")
                            response_text = "يا فنان نورتنا! المهندس جورج معاك، قولي محتاج تعمل جبس بورد فين بالظبط؟"
                        
                        send_fb_message(sender_id, response_text)
                        
    return "ok", 200

def send_fb_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
