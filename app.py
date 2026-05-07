import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# --- الإعدادات ---
# تأكد من وضع المفاتيح بدقة بين علامات التنصيص
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRTLUS3KD5yKTxzamQjJQBNNZArXGiZByKPgVyP7g7AKO7qjuYUZAzbLFBDZBLZByfmdUryaZCFz7s3O9Wr91Uwzn0Rgq3u5StAByiXhiTYeznKZBr0doQvO8JXv271nnWiZApKkSPZBOBoZCs1zvSbc2pxxoOTNNEZBn1A75xsXsp8kRmlmm478OqEKlbaghTJ9ZBnYPdxNX2ywd"
VERIFY_TOKEN = "Gypsum_2026_Secret"
GROQ_API_KEY = "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"

# تهيئة عميل Groq
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
أنت 'جورج'، فنان وصنايعي جبس بورد مصري محترف.
ردودك لازم تكون بلهجة مصرية، شاطرة، وأمينة.
ركز على: (ميزان ليزر، صاج محمل 0.4 و 0.5، خامات كناوف، تسليم على المفتاح).
لو سأل عن السعر: "يا فنان، السعر بيعتمد على الرسمة والمساحة. ابعتلي صورة الشغل اللي عاجبك ومساحة المكان وهعملك أحلى عرض سعر."
هدفنا: إقناع العميل بالمعاينة المجانية.
"""

@app.route("/", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification Failed", 403

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
                                    {"role": "system", "content": SYSTEM_PROMPT},
                                    {"role": "user", "content": user_text}
                                ]
                            )
                            ai_response = completion.choices[0].message.content
                        except Exception as e:
                            # طباعة الغلط في Railway Logs للتصحيح
                            print(f"DEBUG ERROR: {e}")
                            ai_response = "يا فنان نورتنا! المهندس جورج معاك، قولي محتاج تعمل جبس بورد فين بالظبط؟"
                        
                        send_fb_message(sender_id, ai_response)
                        
    return "ok", 200

def send_fb_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, json=payload, headers=headers)

if __name__ == "__main__":
    # استخدام بورت Railway التلقائي
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
