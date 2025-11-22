from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from datetime import datetime
from app.models.pelanggan_model import Pelanggan
from app.models.transakasi_model import Transaksi

transaksi_bp = Blueprint('transaksi', __name__)

@transaksi_bp.route('/transaksi/<uid>', methods=['GET', 'POST'])
@login_required
def transaksi(uid):
    pelanggan = Pelanggan.query.filter_by(uid_rfid=uid).first()
    if not pelanggan:
        flash('Kartu tidak ditemukan!')
        return redirect(url_for('tapping.tapping_page'))

    if request.method == 'POST':
        tipe = request.form.get('tipe')
        nominal = request.form.get('nominal')
        keterangan = request.form.get('keterangan', '')

        if not nominal or float(nominal) <= 0:
            flash('Nominal tidak valid!')
            return redirect(url_for('transaksi.transaksi', uid=uid))

        transaksi = Transaksi(
            id_pelanggan=pelanggan.id,
            id_user=current_user.id,
            tipe=tipe,
            nominal=float(nominal),
            keterangan=keterangan
        )
        db.session.add(transaksi)
        db.session.commit()

        flash(f'Transaksi {tipe} berhasil!')
        return redirect(url_for('tapping.show_tapping', uid=uid))

    return render_template('transaksi_form.html', pelanggan=pelanggan)

@transaksi_bp.route('/topup/<int:id_pelanggan>', methods=['GET', 'POST'])
@login_required
def topup_add(id_pelanggan):
    pelanggan = Pelanggan.query.get_or_404(id_pelanggan)
    
    if request.method == 'POST':
        nominal = request.form.get('nominal', type=float)
        
        if nominal <= 0:
            flash('Nominal Top-Up tidak valid!', 'error')
            return redirect(url_for('transaksi.topup_add', id_pelanggan=id_pelanggan))
        
        transaksi = Transaksi(
            id_pelanggan=id_pelanggan,
            id_user=current_user.id,
            tipe='topup',
            nominal=nominal,
            waktu_transaksi=datetime.now()
        )
        
        db.session.add(transaksi)
        db.session.commit()
        
        flash(f'Saldo sebesar Rp {nominal} berhasil ditambahkan ke {pelanggan.nama_pelanggan}!', 'success')
        return redirect(url_for('tapping.tapping_page', uid=pelanggan.uid_rfid))
    
    return render_template('topup_form.html', pelanggan=pelanggan)