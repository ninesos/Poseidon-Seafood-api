from flask import Flask, request, jsonify, render_template
import json
import random
from linebot import LineBotApi
from linebot.models import TextSendMessage

app = Flask(__name__)

# LINE API setup
line_bot_api = LineBotApi('KBhqBQD9mgE86m3TrRoLtzY5cnmORMMQTd0z1WFmcu9lladnvk+7DSaCRrFgnUieGo1r5MWGUFv3r0pgLj4ITZkZhFlxwj9pUhGCNxQpKmql8hvbp7ocSFlOiutyixMPoH0Yea9C40iWpgHk4cCI3gdB04t89/1O/w1cDnyilFU=')

# ฟังก์ชันส่งข้อมูลการจองไปยัง LINE
def send_to_line(message):
    line_bot_api.push_message('U5f9e64ace2712094d06492483fde6468', TextSendMessage(text=message))

# ฟังก์ชันตรวจสอบจำนวนโต๊ะที่จอง
def check_table_limit(date, table_size):
    with open('reservations.json', 'r') as f:
        reservations = json.load(f)
    count = sum(1 for r in reservations if r['date'] == date and r['table_size'] == table_size)
    limit = 2 if table_size == 'small' else 8
    return count < limit

# หน้าเว็บหลัก
@app.route('/')
def home():
    return render_template('index.html')

# รับข้อมูลการจอง
@app.route('/api/book', methods=['POST'])
def book_table():
    data = request.get_json()
    name = data['name']
    line_id = data['line_id']
    table_size = data['table_size']
    date = data['date']
    time = data['time']

    # ตรวจสอบลิมิตโต๊ะ
    if not check_table_limit(date, table_size):
        return jsonify({'status': 'error', 'message': 'Table limit reached for this date and table size'}), 400

    # สร้างหมายเลขคิว
    queue_number = f"{date.replace('-', '')}-{random.randint(1000, 9999)}"

    # บันทึกข้อมูลการจองลงใน JSON
    with open('reservations.json', 'r') as f:
        reservations = json.load(f)

    reservations.append({
        'name': name,
        'line_id': line_id,
        'table_size': table_size,
        'date': date,
        'time': time,
        'queue_number': queue_number
    })

    with open('reservations.json', 'w') as f:
        json.dump(reservations, f, indent=4)

    # ส่งข้อมูลไปยัง LINE ของแอดมิน
    message = f"New reservation:\nName: {name}\nLINE ID: {line_id}\nTable Size: {table_size}\nDate: {date}\nTime: {time}\nQueue Number: {queue_number}"
    send_to_line(message)

    return jsonify({'status': 'success', 'queue_number': queue_number})

# ดูการจองทั้งหมด
@app.route('/api/reservations', methods=['GET'])
def get_reservations():
    try:
        with open('reservations.json', 'r') as f:
            reservations = json.load(f)
        return jsonify({'status': 'success', 'reservations': reservations})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ลบการจองตามหมายเลขคิว
@app.route('/api/reservations/<queue_number>', methods=['DELETE'])
def delete_reservation(queue_number):
    try:
        with open('reservations.json', 'r') as f:
            reservations = json.load(f)
        
        reservations = [r for r in reservations if r['queue_number'] != queue_number]

        with open('reservations.json', 'w') as f:
            json.dump(reservations, f, indent=4)

        return jsonify({'status': 'success', 'message': f'Reservation with queue number {queue_number} deleted.'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
