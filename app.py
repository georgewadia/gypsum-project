import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# --- 1. الإعدادات ---
# تأكد إنك واضع المفاتيح بدقة بالغة بين علامات التنصيص
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRWqPsd35SgrWib0ssEzJhWrNHvAdGhfmZB098NfkbQvQeVTPZCjh3CvSVAkG0GbS5iKP2CGjg5dBHY7P4zIyga67Jsk9nILlmR9OtZBpUuN3YRxhATBUuj1ZCCnkgAtxZBtAM3JYkUJZAsEeu1Bbbr9hihGvhrGXd8hps2bF0hsjWHx7UePIkUirpHSBTvMcKFnUFcZCaYl"
VERIFY_TOKEN = "Gypsum_2026_Secret"
GROQ_API_KEY = "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"

# تهيئة عميل Groq
client = Groq(api_key=GROQ_API_KEY)

# تعليمات الشخصية
SYSTEM_INSTRUCTIONS = """
أنت 'جورج'، خبير جبس بورد مصري صاحب شركة 'تقنيات الجبس بورد'.
رد بلهجة مصرية ودودة وشاطرة جداً.
ركز في ردودك على: ميزان الليزر للدقة، الصاج المحمل (0.4 و 0.5) للمتانة، وخامات كناوف الأصلية.
إذا سأل العميل عن السعر، قوله: "يا فنان السعر بيختلف حسب التصميم والمساحة، ابعتلي صورة للديزاين اللي عاجبك وأنا هعملك مقايسة مفيش زيها".
حاول دايماً تخليهم يحددوا موعد معاينة مجانية.
"""

@app.route("/", methods=['GET'])
def verify():
    # كود التحقق الخاص بفيسبوك
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
                            # طلب الرد من موديل Llama 3 القوي
                            completion = client.chat.completions.create(
                                model="llama3-8b-8192",
                                messages=[
                                    {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                                    {"role": "user", "content": user_text}
                                ]
                            )
                            ai_answer = completion.choices[0].message.content
                        except Exception as e:
                            # لو في مشكلة في API، اطبعها في الـ Logs وابعث رد بسيط
                            print(f"GROQ ERROR: {e}")
                            ai_answer = "يا فنان نورتنا! المهندس جورج معاك، قولي محتاج تعمل جبس بورد فين بالظبط؟"
                        
                        send_fb_message(sender_id, ai_answer)
                        
    return "ok", 200

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    # تشغيل التطبيق على البورت اللي بيحدده Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
