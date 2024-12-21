from flask import Flask, request, jsonify, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

app = Flask(__name__)

# LINE API Credentials (ใส่ข้อมูลจาก LINE Developers Console)
CHANNEL_ACCESS_TOKEN = "YOUR_CHANNEL_ACCESS_TOKEN"
CHANNEL_SECRET = "YOUR_CHANNEL_SECRET"

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 1. Webhook สำหรับ LINE
@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return jsonify({"message": "Invalid signature"}), 400

    return "OK", 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    # ตอบกลับผู้ใช้
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"คุณส่งข้อความว่า: {user_message}")
    )

    # ส่งข้อความไปหาแอดมิน
    admin_id = "U5f9e64ace2712094d06492483fde6468"  # LINE User ID ที่ต้องการส่งข้อความ
    line_bot_api.push_message(
        admin_id,
        TextSendMessage(text=f"ผู้ใช้ส่งข้อความว่า: {user_message}")
    )

# 2. เส้นทางสำหรับหน้าเว็บ
@app.route("/frontend", methods=["GET"])
def frontend():
    return render_template("index.html")

# 3. เส้นทางสำหรับรับข้อมูลจากหน้าเว็บและส่งไปยัง LINE User
@app.route("/send-to-line", methods=["POST"])
def send_to_line():
    try:
        data = request.json
        message1 = data["message1"]  # ข้อความช่องที่ 1
        message2 = data["message2"]  # ข้อความช่องที่ 2
        option = data["option"]      # ตัวเลือกที่เลือก
        date = data["date"]          # วันที่
        time = data["time"]          # เวลา

        # สร้างข้อความที่จะส่งไปยัง LINE User
        full_message = f"ข้อความ 1: {message1}\nข้อความ 2: {message2}\nตัวเลือก: {option}\nวันที่: {date}\nเวลา: {time}"

        # ส่งข้อความไปยัง LINE User
        admin_id = "U5f9e64ace2712094d06492483fde6468"  # LINE User ID
        line_bot_api.push_message(admin_id, TextSendMessage(text=full_message))
        return jsonify({"status": "success", "message": "Message sent!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

# 4. เส้นทางหน้าหลัก
@app.route("/", methods=["GET"])
def home():
    return "LINE Bot Webhook is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
