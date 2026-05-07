import os
import requests
from flask import Flask, request  # تم تصحيح حرف الـ f هنا ليصبح صغيراً
import google.generativeai as genai

app = Flask(__name__)

# --- الإعدادات ---
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRTLUS3KD5yKTxzamQjJQBNNZArXGiZByKPgVyP7g7AKO7qjuYUZAzbLFBDZBLZByfmdUryaZCFz7s3O9Wr91Uwzn0Rgq3u5StAByiXhiTYeznKZBr0doQvO8JXv271nnWiZApKkSPZBOBoZCs1zvSbc2pxxoOTNNEZBn1A75xsXsp8kRmlmm478OqEKlbaghTJ9ZBnYPdxNX2ywd"
VERIFY_TOKEN = "Gypsum_2026_Secret"
GOOGLE_API_KEY = "AIzaSyBcXiePY5q_sfupFpdg8dlHToiCUfRyqs0"

# تهيئة Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_INSTRUCTIONS = """
أنت 'جورج'، خبير جبس بورد مصري محترف وصاحب شركة 'تقنيات الجبس بورد'.
رد بلهجة مصرية محترمة وودودة (لهجة الصنايعية الشيك).
ركز على: (ميزان ليزر، صاج محمل، خامات كناوف، جودة التشطيب).
السعر: قوله "بيعتمد على التصميم والمساحة، ابعتلي صورة للتصميم أو قولي المساحة كام وأنا هعملك أحلى مقايسة."
حاول تقنع العميل يحدد موعد معاينة.
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
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message") and not messaging_event["message"].get("is_echo"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text")
                    
                    if message_text:
                        print(f"استلمت رسالة: {message_text}")
                        ai_answer = ask_gemini(message_text)
                        send_fb_message(sender_id, ai_answer)
                        
    return "ok", 200

def ask_gemini(user_input):
    try:
        prompt = f"{SYSTEM_INSTRUCTIONS}\nالعميل يسأل: {user_input}"
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text
        else:
            return "منور يا فنان! المهندس جورج معاك، سيب سؤالك ومكانك وهرد عليك بالتفصيل حالا."
            
    except Exception as e:
        print(f"DEBUG: Gemini Error: {e}")
        return "أهلاً بك! المهندس جورج معاك، سيب سؤالك ومكانك وهرد عليك فوراً."

def send_fb_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
