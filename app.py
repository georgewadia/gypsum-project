import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- الإعدادات المحدثة بدقة ---
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABReCN1WQwjZC5I5MAiaFbp5fAq4n1kbYUzBx7UvWZAJBzpAt0Ei84v5RDJEbQEjylkQvVxcF4sp9kytPSFsZBKBPyQQb5VAKgoWBb9Y8ZCxrE34TeMZAgXeNYku8g61qrcyxnMpyojVKjZAwGYwmAhRvxfJa1SfHbGk7EGpPyfnkZCsMKNkr5UhICkw0XOxoZCEhg3rQONrj8"
VERIFY_TOKEN = "Gypsum_2026_Secret"
TOGETHER_API_KEY = "tgp_v1_J_AApC2mmPg9QqEGyPNVntbRhu_nIzRyRbW0g9JgN3M"

SYSTEM_INSTRUCTIONS = """
أنت 'جورج'، خبير جبس بورد مصري محترف وصاحب شركة 'تقنيات الجبس بورد'.
رد بلهجة مصرية عامية ودودة ومحترمة.
نقاط القوة: (ميزان ليزر للدقة، صاج محمل 0.4 و 0.5 للمتانة، خامات كناوف الأصلية).
لو سأل عن السعر: "يا فنان السعر بيختلف حسب التصميم والمساحة، ابعتلي صورة للتصميم اللي عاجبك ومساحة المكان وهعملك أحلى مقايسة".
هدفك: إقناع العميل بتحديد موعد معاينة مجانية.
"""

def get_ai_response(user_text):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "messages": [
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": user_text}
        ],
        "max_tokens": 512,
        "temperature": 0.7
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error calling Together AI: {e}")
        return "منور يا فنان! المهندس جورج معاك، سيب سؤالك ومكانك وهرد عليك بالتفصيل حالا."

@app.route("/", methods=['GET'])
def verify():
    # التحقق من الرابط عند ربطه بفيسبوك
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
                        # الحصول على الرد من الذكاء الاصطناعي
                        ai_answer = get_ai_response(user_text)
                        send_fb_message(sender_id, ai_answer)
                        
    return "ok", 200

def send_fb_message(recipient_id, text):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    # Railway يستخدم بورت 8080 تلقائياً
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
