from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app)

# Line Bot Configuration
LINE_CHANNEL_ACCESS_TOKEN = 'Tb1melP1pi6gJZ3sJv1f1W8jvM21fcKuoKBTNMi7LUgc4HjTen5Egfi0W68QT81BGo1r5MWGUFv3r0pgLj4ITZkZhFlxwj9pUhGCNxQpKmqmzo5Efa8YriPxd9hphle64zQnK2J/ib7OYuaxqFGR0gdB04t89/1O/w1cDnyilFU='
LINE_BOT_API_URL = 'https://api.line.me/v2/bot/message/push'

# In-memory storage for reservations (replace with database in production)
reservations = []

@app.route('/api/reserve', methods=['POST'])
def process_reservation():
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'phone', 'lineId', 'date', 'time']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'status': 'error',
                'missing_field': field
            }), 400
    
    # Store reservation
    reservation = {
        'id': len(reservations) + 1,
        **data
    }
    reservations.append(reservation)
    
    # Send Line Notification
    send_line_notification(reservation)
    
    return jsonify({
        'status': 'success',
        'reservation_id': reservation['id']
    })

def send_line_notification(reservation):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    
    message = f"""Successfully reserved a table! 🐟
🍽️ Booking details 🍽️
Name: {reservation['name']}
Phone: {reservation['phone']}
Line ID: {reservation['lineId']}
Date: {reservation['date']}
Time: {reservation['time']}

Thank you for using Poseidon Seafood."""
    
    payload = {
        'to': reservation['lineId'],  # Assumes Line ID is user's ID
        'messages': [{
            'type': 'text',
            'text': message
        }]
    }
    
    try:
        response = requests.post(LINE_BOT_API_URL, 
                                 headers=headers, 
                                 data=json.dumps(payload))
        return response.json()
    except Exception as e:
        print(f"Error sending Line notification: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True, port=5000)