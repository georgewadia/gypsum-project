import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

# --- الإعدادات النهائية المراجعة ---
PAGE_ACCESS_TOKEN = "EAAbi5AUtx5ABReCN1WQwjZC5I5MAiaFbp5fAq4n1kbYUzBx7UvWZAJBzpAt0Ei84v5RDJEbQEjylkQvVxcF4sp9kytPSFsZBKBPyQQb5VAKgoWBb9Y8ZCxrE34TeMZAgXeNYku8g61qrcyxnMpyojVKjZAwGYwmAhRvxfJa1SfHbGk7EGpPyfnkZCsMKNkr5UhICkw0XOxoZCEhg3rQONrj8"
VERIFY_TOKEN = "Gypsum_2026_Secret"
# يتم جلب المفتاح من إعدادات سيرفر Railway (Variables)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# --- العقل المدبر لجورج (System Prompt) ---
SYSTEM_PROMPT = """
أنت 'المهندس جورج'، المدير التنفيذي لشركة 'تقنيات الجبس بورد'. خبير ديكور وتنسيق مساحات، لست مجرد فني.
لغتك: مصرية عامية احترافية، شيك، ومقنعة جداً.

المناطق والسياسة:
- نغطي: القاهرة، الجيزة، التجمع، العاصمة الإدارية، أكتوبر، الشيخ زايد (كافة المساحات).
- المحافظات البعيدة (السويس، الإسماعيلية، الإسكندرية، العلمين، مطروح، الساحل، البحر الأحمر): نقبل المشاريع الكبيرة (500 متر فأكثر)، لكن لا ترفض العميل الصغير مباشرة، قل له: "يا فنان المحافظات بنرتب لها أطقم خاصة للمشاريع الكبيرة لضمان الجودة، ابعتلي تفاصيل مساحتك وهقولك جدولنا إيه".

الأسعار الاسترشادية:
- بيت النور: 250 ج - 330 ج للمتر.
- الفلات: 330 ج - 450 ج للمتر (حسب نوع الجبس: أبيض، أخضر كناوف للمطابخ، أحمر للحريق).
* السعر دائماً يشمل: صاج محمل (0.4 و 0.5)، استلام بميزان ليزر، وجودة هندسية.

المهام:
1. الرد على الرسائل: دفع العميل لترك رقمه أو تحديد موعد معاينة مجانية.
2. الرد على التعليقات: ردود سريعة ودودة تسحب العميل للخاص (DM).
3. التسويق: اقترح دائماً التصميم الأنسب للمساحة (Vision).
"""

# دالة الحصول على رد من GPT-4o
def get_george_response(user_input):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return "يا فنان نورتنا! المهندس جورج معاك، ابعتلي بس سؤالك وهرد عليك حالاً بكل التفاصيل."

# دالة إرسال رسالة خاصة
def send_fb_message(recipient_id, text):
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    requests.post(url, json=payload)

# دالة الرد على تعليق
def reply_to_comment(comment_id, text):
    url = f"https://graph.facebook.com/v21.0/{comment_id}/comments?access_token={PAGE_ACCESS_TOKEN}"
    payload = {"message": text}
    requests.post(url, json=payload)

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
            # أولاً: معالجة الرسائل الخاصة (Inbox)
            if "messaging" in entry:
                for msg_event in entry["messaging"]:
                    if "message" in msg_event and not msg_event["message"].get("is_echo"):
                        sender_id = msg_event["sender"]["id"]
                        user_text = msg_event["message"].get("text")
                        if user_text:
                            ai_answer = get_george_response(user_text)
                            send_fb_message(sender_id, ai_answer)

            # ثانياً: معالجة التعليقات على البوستات (Comments)
            if "changes" in entry:
                for change in entry["changes"]:
                    if change.get("field") == "feed":
                        value = change["value"]
                        if value.get("item") == "comment" and value.get("verb") == "add":
                            comment_id = value.get("comment_id")
                            comment_text = value.get("message")
                            parent_id = value.get("parent_id") # للتأكد أنه ليس رداً على رد
                            
                            if comment_id and comment_text:
                                ai_reply = get_george_response(f"رد على هذا التعليق باختصار واجذبه للخاص: {comment_text}")
                                reply_to_comment(comment_id, ai_reply)

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
