# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User, db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
    
#     if request.method == 'POST':
#         try:
#             # Validasi dengan Pydantic schema
#             login_data = UserLogin(
#                 username=request.form['username'],
#                 password=request.form['password']
#             )
            
#             # Cari user di database
#             user = User.query.filter_by(username=login_data.username).first()
            
#             if user and user.check_password(login_data.password):
#                 if user.is_active:
#                     login_user(user)
#                     flash('Login berhasil!', 'success')
#                     next_page = request.args.get('next')
#                     return redirect(next_page or url_for('main.index'))
#                 else:
#                     flash('Akun tidak aktif', 'danger')
#             else:
#                 flash('Username atau password salah', 'danger')
                
#         except Exception as e:
#             flash(f'Error: {str(e)}', 'danger')
    
#     return render_template('auth/login.html')

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
    
#     if request.method == 'POST':
#         try:
#             # Validasi dengan Pydantic schema
#             user_data = UserCreate(
#                 username=request.form['username'],
#                 email=request.form['email'],
#                 password=request.form['password'],
#                 password_confirm=request.form['password_confirm']
#             )
            
#             # Cek apakah username atau email sudah ada
#             if User.query.filter_by(username=user_data.username).first():
#                 flash('Username sudah digunakan', 'danger')
#                 return render_template('auth/register.html')
            
#             if User.query.filter_by(email=user_data.email).first():
#                 flash('Email sudah digunakan', 'danger')
#                 return render_template('auth/register.html')
            
#             # Buat user baru
#             user = User(
#                 username=user_data.username,
#                 email=user_data.email
#             )
#             user.set_password(user_data.password)
            
#             db.session.add(user)
#             db.session.commit()
            
#             flash('Registrasi berhasil! Silakan login.', 'success')
#             return redirect(url_for('auth.login'))
            
#         except Exception as e:
#             db.session.rollback()
#             flash(f'Error: {str(e)}', 'danger')
    
#     return render_template('auth/register.html')

# @auth_bp.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('Anda telah logout', 'info')
#     return redirect(url_for('main.index'))

# @auth_bp.route('/profile')
# @login_required
# def profile():
#     return render_template('auth/profile.html', user=current_user)