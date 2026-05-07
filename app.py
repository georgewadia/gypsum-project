import os
import requests
from flask import Flask, request
from groq import Groq

app = Flask(__name__)

# --- الإعدادات ---
# حط مفاتيحك هنا مباشرة بين علامات التنصيص
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABRTLUS3KD5yKTxzamQjJQBNNZArXGiZByKPgVyP7g7AKO7qjuYUZAzbLFBDZBLZByfmdUryaZCFz7s3O9Wr91Uwzn0Rgq3u5StAByiXhiTYeznKZBr0doQvO8JXv271nnWiZApKkSPZBOBoZCs1zvSbc2pxxoOTNNEZBn1A75xsXsp8kRmlmm478OqEKlbaghTJ9ZBnYPdxNX2ywd"
VERIFY_TOKEN = "Gypsum_2026_Secret"
GROQ_API_KEY = "حط_هنا_مفتاح_GROQ_الجديد"

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_INSTRUCTIONS = "أنت جورج خبير جبس بورد مصري. رد بلهجة مصرية شاطرة عن الميزان الليزر والصاج المحمل وخامات كناوف. لو حد سأل عن السعر قوله ابعتلي صورة للتصميم ومساحة الشقة وهعملك مقايسة."

@app.route("/", methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "failed", 403

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
                        print(f"Error: {e}")
                        ai_answer = "يا فنان نورتنا! المهندس جورج معاك، قولي محتاج تعمل جبس بورد فين بالظبط؟"

                    send_fb_message(sender_id, ai_answer)
    return "ok", 200

def send_fb_message(pid, txt):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": pid}, "message": {"text": txt}})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
