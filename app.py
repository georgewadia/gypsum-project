import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# --- الإعدادات (المفاتيح المخفية) ---
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABReCN1WQwjZC5I5MAiaFbp5fAq4n1kbYUzBx7UvWZAJBzpAt0Ei84v5RDJEbQEjylkQvVxcF4sp9kytPSFsZBKBPyQQb5VAKgoWBb9Y8ZCxrE34TeMZAgXeNYku8g61qrcyxnMpyojVKjZAwGYwmAhRvxfJa1SfHbGk7EGpPyfnkZCsMKNkr5UhICkw0XOxoZCEhg3rQONrj8"
VERIFY_TOKEN = "Gypsum_2026_Secret"

# هنا بنقول للكود: روح اقرأ المفتاح من إعدادات Railway مش من هنا
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
أنت 'جورج'، فنان جبس بورد مصري محترف. ردودك عامية مصرية، شاطرة، وبتركز على ميزان الليزر وصاج كناوف المحمل.
لو سأل عن السعر قوله: "يا فنان السعر حسب التصميم والمساحة، ابعت صورة وهعملك أحلى مقايسة".
هدفنا: تحديد موعد معاينة مجانية.
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
                    
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": user_text}
                            ]
                        )
                        ai_answer = response.choices[0].message.content
                    except Exception as e:
                        print(f"OpenAI Error: {e}")
                        ai_answer = "منور يا فنان! المهندس جورج معاك، سيب سؤالك وهرد عليك حالا."

                    send_fb_message(sender_id, ai_answer)
    return "ok", 200

def send_fb_message(pid, txt):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": pid}, "message": {"text": txt}})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
