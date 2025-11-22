from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.user_model import User
from app import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template(
        'dashboard.html',
        nama_user=current_user.nama_user,
        role=current_user.role
    )


@user_bp.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('Akses ditolak: hanya admin yang bisa mengakses data user.', 'danger')
        return redirect(url_for('user.dashboard'))

    users = User.query.all()
    return render_template('users.html', users=users)


@user_bp.route('/users/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('user.dashboard'))

    nik_user = request.form['nik_user']
    nama_user = request.form['nama_user']
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']

    if User.query.filter_by(username=username).first():
        flash('Username sudah digunakan!', 'warning')
        return redirect(url_for('user.users'))

    user = User(
        nik_user=nik_user,
        nama_user=nama_user,
        username=username,
        role=role
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()
    flash('User berhasil ditambahkan!', 'success')
    return redirect(url_for('user.users'))


@user_bp.route('/users/edit/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin':
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('user.dashboard'))

    user = User.query.get_or_404(id)
    user.nik_user = request.form['nik_user']
    user.nama_user = request.form['nama_user']
    user.username = request.form['username']
    user.role = request.form['role']

    password = request.form.get('password')
    if password:
        user.set_password(password)

    db.session.commit()
    flash('User berhasil diperbarui!', 'success')
    return redirect(url_for('user.users'))


@user_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'admin':
        flash('Akses ditolak.', 'danger')
        return redirect(url_for('user.dashboard'))

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User berhasil dihapus!', 'info')
    return redirect(url_for('user.users'))
