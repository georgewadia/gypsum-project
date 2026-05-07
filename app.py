import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# --- الإعدادات النهائية ---
# 1. توكن فيسبوك (الذي يربط الكود بصفحتك)
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRTLUS3KD5yKTxzamQjJQBNNZArXGiZByKPgVyP7g7AKO7qjuYUZAzbLFBDZBLZByfmdUryaZCFz7s3O9Wr91Uwzn0Rgq3u5StAByiXhiTYeznKZBr0doQvO8JXv271nnWiZApKkSPZBOBoZCs1zvSbc2pxxoOTNNEZBn1A75xsXsp8kRmlmm478OqEKlbaghTJ9ZBnYPdxNX2ywd"

# 2. توكن التحقق (الذي تكتبه داخل إعدادات Webhook فيسبوك)
VERIFY_TOKEN = "Gypsum_2026_Secret"

# 3. مفتاح Groq (العقل المفكر للبوت)
# نصيحة: لو تقدر تعمل مفتاح جديد من Groq Console هيكون أضمن
GROQ_API_KEY = "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"

# تهيئة الاتصال بـ Groq
client = Groq(api_key=GROQ_API_KEY)

# تعليمات الشخصية (جورج الصنايعي الشاطر)
SYSTEM_PROMPT = """
أنت 'جورج'، فنان وصنايعي جبس بورد مصري محترف وصاحب شركة 'تقنيات الجبس بورد'.
ردودك دايماً بلهجة مصرية عامية، محترمة، وشاطرة. 
ركز على: ميزان ليزر للدقة، صاج محمل (0.4 و 0.5)، وخامات كناوف الأصلية.
لو سأل عن السعر: "يا فنان السعر بيختلف حسب التصميم والمساحة، ابعتلي صورة للديزاين اللي عاجبك وأنا هعملك مقايسة مفيش زيها".
حاول دايماً تخليهم يحددوا موعد معاينة مجانية في التجمع أو أي مكان.
"""

@app.route("/", methods=['GET'])
def verify():
    # كود التحقق الإلزامي لفيسبوك
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "خطأ في التحقق", 403

@app.route("/", methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data["entry"]:
            for messaging_event in entry.get("messaging", []):
                # التأكد أن الرسالة قادمة من مستخدم وليست صدى (Echo)
                if messaging_event.get("message") and not messaging_event["message"].get("is_echo"):
                    sender_id = messaging_event["sender"]["id"]
                    user_text = messaging_event["message"].get("text")
                    
                    if user_text:
                        try:
                            # استدعاء الذكاء الاصطناعي Groq
                            completion = client.chat.completions.create(
                                model="llama3-8b-8192",
                                messages=[
                                    {"role": "system", "content": SYSTEM_PROMPT},
                                    {"role": "user", "content": user_text}
                                ]
                            )
                            response_text = completion.choices[0].message.content
                        except Exception as e:
                            # في حالة حدوث أي خطأ في API، يطبع هنا ويرد بالرد التلقائي
                            print(f"Error logic: {e}")
                            response_text = "يا فنان نورتنا! المهندس جورج معاك، قولي محتاج تعمل جبس بورد فين بالظبط؟"
                        
                        send_fb_message(sender_id, response_text)
                        
    return "ok", 200

def send_fb_message(recipient_id, text):
    # دالة إرسال الرد لفيسبوك
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    # تشغيل السيرفر على بورت Railway التلقائي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
