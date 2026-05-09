import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# --- الإعدادات المحدثة ---
# رمز الصفحة اللي بعته
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABReCN1WQwjZC5I5MAiaFbp5fAq4n1kbYUzBx7UvWZAJBzpAt0Ei84v5RDJEbQEjylkQvVxcF4sp9kytPSFsZBKBPyQQb5VAKgoWBb9Y8ZCxrE34TeMZAgXeNYku8g61qrcyxnMpyojVKjZAwGYwmAhRvxfJa1SfHbGk7EGpPyfnkZCsMKNkr5UhICkw0XOxoZCEhg3rQONrj8"
# توكن التحقق الخاص بك
VERIFY_TOKEN = "Gypsum_2026_Secret"
# مفتاح Groq الجديد
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

# شخصية البوت (جورج)
SYSTEM_PROMPT = """
أنت 'جورج'، خبير جبس بورد مصري محترف وصاحب شركة 'تقنيات الجبس بورد'.
رد بلهجة مصرية عامية شاطرة وأمينة. 
ركز على: (ميزان ليزر للدقة، صاج محمل 0.4 و 0.5، خامات كناوف الأصلية).
لو سأل عن السعر: "يا فنان السعر بيعتمد على الرسمة والمساحة. ابعتلي صورة الشغل اللي عاجبك ومساحة المكان وهعملك أحلى مقايسة."
هدفك: إقناع العميل بالمعاينة المجانية.
"""

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
            for msg_event in entry.get("messaging", []):
                if "message" in msg_event and "text" in msg_event["message"] and not msg_event["message"].get("is_echo"):
                    sender_id = msg_event["sender"]["id"]
                    user_text = msg_event["message"]["text"]
                    
                    if user_text:
                        try:
                            # استخدام الموديل الأحدث llama-3.3-70b-versatile
                            completion = client.chat.completions.create(
                                model="llama-3.3-70b-versatile",
                                messages=[
                                    {"role": "system", "content": SYSTEM_PROMPT},
                                    {"role": "user", "content": user_text}
                                ]
                            )
                            ai_answer = completion.choices[0].message.content
                        except Exception as e:
                            print(f"Error logic: {e}")
                            ai_answer = "يا فنان نورتنا! المهندس جورج معاك، قولي محتاج تعمل جبس بورد فين بالظبط؟"

                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def send_fb_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
