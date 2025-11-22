from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.pelanggan_model import Pelanggan
from app import db
import uuid

pelanggan_bp = Blueprint('pelanggan', __name__)


def generate_uid():
    # Sementara, UID RFID digenerate otomatis (bisa diganti saat ESP32 siap)
    return str(uuid.uuid4())[:8].upper()


@pelanggan_bp.route('/pelanggan')
@login_required
def pelanggan_list():
    q = request.args.get('q')
    if q:
        data = Pelanggan.query.filter(
            (Pelanggan.nama_pelanggan.like(f"%{q}%")) |
            (Pelanggan.nik_pelanggan.like(f"%{q}%"))
        ).all()
    else:
        data = Pelanggan.query.all()

    return render_template('pelanggan_list.html', pelanggan=data, q=q)


@pelanggan_bp.route('/pelanggan/add', methods=['GET', 'POST'])
@login_required
def pelanggan_add():
    if request.method == 'POST':
        uid_rfid = request.form.get('uid_rfid') or generate_uid()
        nik_pelanggan = request.form['nik_pelanggan']
        nama_pelanggan = request.form['nama_pelanggan']
        kelas = request.form['kelas']
        no_hp = request.form['no_hp']

        pelanggan = Pelanggan(
            uid_rfid=uid_rfid,
            nik_pelanggan=nik_pelanggan,
            nama_pelanggan=nama_pelanggan,
            kelas=kelas,
            no_hp=no_hp
        )

        db.session.add(pelanggan)
        db.session.commit()
        flash("Pelanggan berhasil ditambahkan!", "success")
        return redirect(url_for('pelanggan.pelanggan_list'))

    return render_template('pelanggan_add.html')


@pelanggan_bp.route('/pelanggan/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def pelanggan_edit(id):
    pelanggan = Pelanggan.query.get_or_404(id)

    if request.method == 'POST':
        pelanggan.nik_pelanggan = request.form['nik_pelanggan']
        pelanggan.nama_pelanggan = request.form['nama_pelanggan']
        pelanggan.kelas = request.form['kelas']
        pelanggan.no_hp = request.form['no_hp']

        db.session.commit()
        flash("Pelanggan berhasil diperbarui!", "success")
        return redirect(url_for('pelanggan.pelanggan_list'))

    return render_template('pelanggan_edit.html', pelanggan=pelanggan)


@pelanggan_bp.route('/pelanggan/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def pelanggan_delete(id):
    pelanggan = Pelanggan.query.get_or_404(id)
    db.session.delete(pelanggan)
    db.session.commit()
    flash("Pelanggan berhasil dihapus.", "info")
    return redirect(url_for('pelanggan.pelanggan_list'))

@pelanggan_bp.route('/api/get_uid')
@login_required
def get_uid():
    # ambil UID terakhir yang dikirim ESP32 (disimpan di cache DB / global)
    from app import last_uid_cache  
    return {"uid": last_uid_cache or ""}
