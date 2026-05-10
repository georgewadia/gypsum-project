import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# --- الإعدادات النهائية المدمجة ---
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABReCN1WQwjZC5I5MAiaFbp5fAq4n1kbYUzBx7UvWZAJBzpAt0Ei84v5RDJEbQEjylkQvVxcF4sp9kytPSFsZBKBPyQQb5VAKgoWBb9Y8ZCxrE34TeMZAgXeNYku8g61qrcyxnMpyojVKjZAwGYwmAhRvxfJa1SfHbGk7EGpPyfnkZCsMKNkr5UhICkw0XOxoZCEhg3rQONrj8"
VERIFY_TOKEN = "Gypsum_2026_Secret"
OPENAI_API_KEY = "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"

client = OpenAI(api_key=OPENAI_API_KEY)

# تطوير الشخصية: "جورج" المهندس الفنان
SYSTEM_PROMPT = """
أنت 'جورج'، مهندس وخبير جبس بورد مصري محترف جداً، صاحب شركة 'تقنيات الجبس بورد'.
تحدث بلهجة مصرية عامية، ذكية، وودودة.
نقاط القوة التي تركز عليها: 
1. الاستلام بميزان ليزر (على الشعرة).
2. استخدام صاج محمل (0.4 و 0.5) لضمان عدم حدوث شروخ أو "ترريح" في السقف.
3. خامات كناوف (Knauf) الأصلية والخضراء للمناطق الرطبة.
4. الالتزام بالمواعيد وسرعة التنفيذ.

إذا سأل العميل عن السعر: "يا فنان السعر بيختلف حسب التصميم والمساحة وكمية الديكور. ابعتلي صورة الديزاين اللي عاجبك ومكان الشقة وهعملك مقايسة هندسية محترمة."
هدفك دايماً: تحديد موعد لمعاينة المكان على الطبيعة مجاناً.
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
                        # طلب الرد من GPT-4o
                        response = client.chat.completions.create(
                            model="gpt-4o", # الموديل الأحدث والأذكى
                            messages=[
                                {"role": "system", "content": SYSTEM_PROMPT},
                                {"role": "user", "content": user_text}
                            ],
                            temperature=0.7 # ليعطي ردوداً طبيعية وغير متكررة
                        )
                        ai_answer = response.choices[0].message.content
                    except Exception as e:
                        print(f"OpenAI Error: {e}")
                        ai_answer = "يا فنان نورتنا! المهندس جورج معاك، ابعتلي طلبك وهرد عليك فوراً بكل التفاصيل اللي محتاجها."

                    send_fb_message(sender_id, ai_answer)
    return "ok", 200

def send_fb_message(pid, txt):
    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    requests.post(url, json={"recipient": {"id": pid}, "message": {"text": txt}})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
