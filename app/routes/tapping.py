from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from app.models.user_model import User
from app.models.pelanggan_model import Pelanggan
from app.models.transakasi_model import Transaksi
from app import db
from flask_login import login_required
import os

tapping_bp = Blueprint('tapping', __name__)

@tapping_bp.route('/api/tapping/<uid>', methods=['GET'])
@login_required
def tapping_api(uid):
    pelanggan = Pelanggan.query.filter_by(uid_rfid=uid).first()

    if not pelanggan:
        return jsonify({'status': 'error', 'message': 'Kartu belum terdaftar'}), 404

    # Hitung saldo dari transaksi
    saldo_topup = (
        db.session.query(db.func.sum(Transaksi.nominal))
        .filter_by(id_pelanggan=pelanggan.id, tipe='topup')
        .scalar() or 0
    )
    saldo_keluar = (
        db.session.query(db.func.sum(Transaksi.nominal))
        .filter_by(id_pelanggan=pelanggan.id, tipe='pembelian')
        .scalar() or 0
    )
    saldo = saldo_topup - saldo_keluar

    return jsonify({
        'status': 'success',
        'data': {
            'id': pelanggan.id,
            'nama': pelanggan.nama_pelanggan,
            'kelas': pelanggan.kelas,
            'no_hp': pelanggan.no_hp,
            'uid_rfid': pelanggan.uid_rfid,
            'saldo': float(saldo)
        }
    })
    
# @tapping_bp.route('/tapping/<uid>', methods=['GET'])
# @login_required
# def tapping_page(uid):
#     pelanggan = Pelanggan.query.filter_by(uid_rfid=uid).first()

#     if not pelanggan:
#         flash('Kartu belum terdaftar. Silakan daftarkan pelanggan terlebih dahulu.', 'error')
#         return redirect(url_for('pelanggan.pelanggan_list'))

#     saldo_topup = (
#         db.session.query(db.func.sum(Transaksi.nominal))
#         .filter_by(id_pelanggan=pelanggan.id, tipe='topup')
#         .scalar() or 0
#     )
#     saldo_keluar = (
#         db.session.query(db.func.sum(Transaksi.nominal))
#         .filter_by(id_pelanggan=pelanggan.id, tipe='pembelian')
#         .scalar() or 0
#     )
#     saldo = saldo_topup - saldo_keluar

#     return render_template('tapping_detail.html', pelanggan=pelanggan, saldo=saldo)

@tapping_bp.route('/tapping', methods=['GET', 'POST'])
@login_required
def tapping_page():
    if request.method == 'POST':
        uid = request.form.get('uid')
        return redirect(url_for('tapping.show_tapping', uid=uid))
    return render_template('tapping_input.html')

@tapping_bp.route('/tapping/<uid>')
@login_required
def show_tapping(uid):
    pelanggan = Pelanggan.query.filter_by(uid_rfid=uid).first()
    if not pelanggan:
        flash('Kartu belum terdaftar!')
        return redirect(url_for('tapping.tapping_page'))

    saldo_topup = db.session.query(db.func.sum(Transaksi.nominal)).filter_by(id_pelanggan=pelanggan.id, tipe='topup').scalar() or 0
    saldo_keluar = db.session.query(db.func.sum(Transaksi.nominal)).filter_by(id_pelanggan=pelanggan.id, tipe='pembelian').scalar() or 0
    saldo = saldo_topup - saldo_keluar

    return render_template('tapping_detail.html', pelanggan=pelanggan, saldo=saldo)

@tapping_bp.route('/api/tapping', methods=['POST'])
def tapping_receive():
    data = request.get_json()
    uid = data.get('uid')

    if not uid:
        return jsonify({"status": "error", "message": "UID tidak diberikan"}), 400

    # Simpan UID ke memory sederhana (redis recommended)
    with open("last_uid.txt", "w") as f:
        f.write(uid)

    return jsonify({"status": "success"})

@tapping_bp.route('/api/last-uid', methods=['GET'])
def get_last_uid():
    if not os.path.exists("last_uid.txt"):
        return jsonify({"uid": None})

    with open("last_uid.txt", "r") as f:
        uid = f.read().strip()

    # Setelah dibaca, kosongkan biar tidak redirect ulang
    open("last_uid.txt", "w").close()

    return jsonify({"uid": uid})

