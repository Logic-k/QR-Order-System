from flask import Flask, request, jsonify, render_template_string
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Firebase 연결
cred = credentials.Certificate("test-a829c-firebase-adminsdk-fbsvc-b0d1a4414c.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 주문 페이지 (QR 코드로 이동)
@app.route("/order", methods=["GET", "POST"])
def order():
    seat_number = request.args.get("seat", "1")

    if request.method == "POST":
        data = request.json
        order_data = {
            "seat": seat_number,
            "salt": data.get("saltType"),
            "drink": data.get("drink"),
            "status": "대기 중"
        }
        db.collection("orders").add(order_data)
        return jsonify({"message": "주문이 완료되었습니다!"})

    return render_template_string('''
    <html>
    <head>
        <title>QR 주문</title>
        <script>
            function placeOrder() {
                let salt = document.getElementById('salt').value;
                let drink = document.getElementById('drink').value;
                fetch(window.location.href, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ saltType: salt, drink: drink })
                }).then(res => res.json()).then(data => alert(data.message));
            }
        </script>
    </head>
    <body>
        <h2>자리 {{ seat_number }}번 주문</h2>
        <label>족욕 소금 선택:</label>
        <select id="salt"><option value="라벤더">라벤더</option><option value="녹차">녹차</option></select><br/>
        <label>음료 선택:</label>
        <select id="drink"><option value="커피">커피</option><option value="차">차</option></select><br/>
        <button onclick="placeOrder()">주문하기</button>
    </body>
    </html>
    ''', seat_number=seat_number)

# 관리자 페이지 (주문 목록 확인)
@app.route("/admin")
def admin():
    orders = db.collection("orders").stream()
    order_list = [f"자리 {o.get('seat')}: {o.get('salt')}, {o.get('drink')} ({o.get('status')})" for o in orders]
    
    return "<br>".join(order_list) + '''<br><br><a href="/admin">새로고침</a>'''

if __name__ == "__main__":
    app.run(debug=True)
