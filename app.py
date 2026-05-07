import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# --- الإعدادات ---
# تأكد من صحة هذه البيانات من صفحة Meta Developers و Google AI Studio
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRTLUS3KD5yKTxzamQjJQBNNZArXGiZByKPgVyP7g7AKO7qjuYUZAzbLFBDZBLZByfmdUryaZCFz7s3O9Wr91Uwzn0Rgq3u5StAByiXhiTYeznKZBr0doQvO8JXv271nnWiZApKkSPZBOBoZCs1zvSbc2pxxoOTNNEZBn1A75xsXsp8kRmlmm478OqEKlbaghTJ9ZBnYPdxNX2ywd"
VERIFY_TOKEN = "Gypsum_2026_Secret"
GOOGLE_API_KEY = "AIzaSyBcXiePY5q_sfupFpdg8dlHToiCUfRyqs0"

# تهيئة موديل Gemini (استخدام نسخة 1.5 Flash الأسرع)
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"CRITICAL: Failed to configure Gemini: {e}")

SYSTEM_INSTRUCTIONS = """
أنت 'جورج'، خبير جبس بورد مصري محترف وصاحب شركة 'تقنيات الجبس بورد'.
رد بلهجة مصرية محترمة وودودة.
نقاط القوة: (ميزان ليزر، صاج محمل 0.4 و 0.5، خامات كناوف الأصلية، دقة في المواعيد).
لو سأل عن السعر: "السعر بيتحسب بناءً على التصميم والمساحة، ابعتلي صورة للتصميم أو قولي مساحة الشقة وهعملك أحلى مقايسة."
هدفنا: إقناع العميل بتحديد موعد معاينة مجانية في التجمع أو أي مكان.
"""

@app.route("/", methods=['GET'])
def verify():
    # التحقق من الرابط عند ربطه بفيسبوك لأول مرة
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
                        print(f"Received message from {sender_id}: {user_text}")
                        ai_answer = ask_gemini(user_text)
                        send_fb_message(sender_id, ai_answer)
                        
    return "ok", 200

def ask_gemini(user_input):
    try:
        # صياغة الطلب لـ Gemini
        full_prompt = f"{SYSTEM_INSTRUCTIONS}\nالعميل يسأل: {user_text}"
        response = model.generate_content(full_prompt)
        
        if response and response.text:
            return response.text
        else:
            return "منور يا فنان! ثواني والمهندس جورج هيتواصل معاك فوراً."
            
    except Exception as e:
        # هذا السطر سيطبع لك الخطأ الحقيقي في Railway Logs
        print(f"DEBUG: Gemini API Error: {e}")
        return "منور يا فنان! المهندس جورج معاك، سيب سؤالك ومكانك وهرد عليك بالتفصيل حالا."

def send_fb_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    try:
        r = requests.post(url, json=payload)
        print(f"FB Message Status: {r.status_code}")
    except Exception as e:
        print(f"Error sending message to FB: {e}")

if __name__ == "__main__":
    # Railway يستخدم بورت 8080 تلقائياً في أغلب الأحيان
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
