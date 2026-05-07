import os
import requests
from flask import Flask, request
import google.generativeai as genai

app = Flask(__name__)

# --- الإعدادات ---
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRTLUS3KD5yKTxzamQjJQBNNZArXGiZByKPgVyP7g7AKO7qjuYUZAzbLFBDZBLZByfmdUryaZCFz7s3O9Wr91Uwzn0Rgq3u5StAByiXhiTYeznKZBr0doQvO8JXv271nnWiZApKkSPZBOBoZCs1zvSbc2pxxoOTNNEZBn1A75xsXsp8kRmlmm478OqEKlbaghTJ9ZBnYPdxNX2ywd"
VERIFY_TOKEN = "Gypsum_2026_Secret"
GOOGLE_API_KEY = "AIzaSyBcXiePY5q_sfupFpdg8dlHToiCUfRyqs0"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_INSTRUCTIONS = """
أنت مساعد ذكي لشركة 'تقنيات الجبس بورد' في مصر. 
مديرك هو المهندس جورج. 
قواعد الرد:
1. رد بلهجة مصرية مهذبة ومحترفة.
2. ركز على الجودة (استخدام ميزان الليزر، الصاج المحمل، خامات كناوف الأصلية).
3. لو العميل سأل عن السعر، اطلب منه مساحة المكان أو صورة للتصميم لتقديم مقايسة دقيقة.
4. هدفك هو إقناع العميل بتحديد موعد معاينة مجانية.
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
                    user_text = messaging_event["message"].get("text")
                    if user_text:
                        ai_answer = ask_gemini(user_text)
                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def ask_gemini(user_input):
    try:
        response = model.generate_content(f"{SYSTEM_INSTRUCTIONS}\nالعميل: {user_input}")
        return response.text
    except Exception as e:
        print(f"Error: {e}")
        return "أهلاً بك! المهندس جورج معاك، سيب سؤالك ومكانك وهرد عليك فوراً."

def send_fb_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    # هذا السطر ضروري ليعمل الكود على Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
