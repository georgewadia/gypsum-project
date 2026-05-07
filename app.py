import os
import requests
from flask import Flask, request
from google import genai

app = Flask(__name__)

# --- الإعدادات ---
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRTLUS3KD5yKTxzamQjJQBNNZArXGiZByKPgVyP7g7AKO7qjuYUZAzbLFBDZBLZByfmdUryaZCFz7s3O9Wr91Uwzn0Rgq3u5StAByiXhiTYeznKZBr0doQvO8JXv271nnWiZApKkSPZBOBoZCs1zvSbc2pxxoOTNNEZBn1A75xsXsp8kRmlmm478OqEKlbaghTJ9ZBnYPdxNX2ywd"
VERIFY_TOKEN = "Gypsum_2026_Secret"
GOOGLE_API_KEY = "AIzaSyBcXiePY5q_sfupFpdg8dlHToiCUfRyqs0"

client = genai.Client(api_key=GOOGLE_API_KEY)

SYSTEM_INSTRUCTIONS = "أنت جورج خبير جبس بورد مصري. رد بلهجة مصرية محترفة عن الديكور والأسعار والجودة."

@app.route("/", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Failed", 403

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
                            # الطريقة الجديدة لطلب الرد من جوجل
                            response = client.models.generate_content(
                                model="gemini-1.5-flash", 
                                contents=f"{SYSTEM_INSTRUCTIONS}\nالعميل: {user_text}"
                            )
                            ai_answer = response.text
                        except Exception as e:
                            print(f"Error calling Gemini: {e}")
                            ai_answer = "منور يا فنان! المهندس جورج معاك، سيب سؤالك وهرد عليك فوراً."
                        
                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def send_fb_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
