import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# --- الإعدادات ---
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRTLUS3KD5yKTxzamQjJQBNNZArXGiZByKPgVyP7g7AKO7qjuYUZAzbLFBDZBLZByfmdUryaZCFz7s3O9Wr91Uwzn0Rgq3u5StAByiXhiTYeznKZBr0doQvO8JXv271nnWiZApKkSPZBOBoZCs1zvSbc2pxxoOTNNEZBn1A75xsXsp8kRmlmm478OqEKlbaghTJ9ZBnYPdxNX2ywd"
VERIFY_TOKEN = "Gypsum_2026_Secret"
GROQ_API_KEY = "AIzaSyBcXiePY5q_sfupFpdg8dlHToiCUfRyqs0" # تأكد إن ده مفتاح Groq مش جوجل

client = Groq(api_key="gsk_xxxxxxxxxxxx") # حط هنا مفتاح Groq اللي يبدأ بـ gsk

SYSTEM_INSTRUCTIONS = """
أنت 'جورج'، خبير جبس بورد مصري محترف. 
رد بلهجة مصرية "شيك" ومقنعة. 
ركز على إننا بنستخدم ميزان ليزر وصاج محمل (0.4 و 0.5) وخامات كناوف. 
لو حد سأل عن السعر، قوله: "السعر بيعتمد على التصميم والمساحة، ابعتلي صورة للتصميم أو مساحة الشقة وهعملك أحلى مقايسة". 
حاول دايماً تخليهم يحددوا موعد معاينة.
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
                        try:
                            # التعديل هنا: اسم الموديل الجديد
                            chat_completion = client.chat.completions.create(
                                messages=[
                                    {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                                    {"role": "user", "content": user_text}
                                ],
                                model="llama-3.1-8b-instant", 
                            )
                            ai_answer = chat_completion.choices[0].message.content
                        except Exception as e:
                            print(f"Error: {e}")
                            ai_answer = "أهلاً بك! المهندس جورج معاك، سيب سؤالك ومكانك وهرد عليك فوراً."
                        
                        send_fb_message(sender_id, ai_answer)
    return "ok", 200

def send_fb_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
