from flask import Blueprint, render_template, jsonify, request

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('login.html')

@main.route('/api/frid/scan', methods=['POST'])
def scan_rfid():
    data = request.json
    uid = data.get('uid')
    
    return jsonify({
        "nama_pelanggan": "Rina",
        "saldo": 15000,
        "status": "OK",
        "uid": uid
    })