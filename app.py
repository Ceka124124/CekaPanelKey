from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Kullanıcı Modeli
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Key Modeli
class Key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    key_value = db.Column(db.String(256), unique=True, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ana Sayfa
@app.route('/')
def home():
    return "Ana Sayfa"

# Kullanıcı Kaydı
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Bu kullanıcı adı zaten mevcut!", "danger")
            return redirect(url_for('register'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Başarıyla kayıt oldunuz!", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Kullanıcı Girişi
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash("Başarıyla giriş yaptınız!", "success")
            return redirect(url_for('generate'))
        else:
            flash("Kullanıcı adı veya şifre hatalı!", "danger")
    
    return render_template('login.html')

# Key Oluşturma
@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    if request.method == 'POST':
        key_type = request.form['key_type']

        if key_type == "random":
            key_value = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        elif key_type == "custom":
            key_value = request.form['custom_key']
        else:
            flash("Geçersiz key türü!", "danger")
            return redirect(url_for('generate'))

        new_key = Key(user_id=current_user.id, key_value=key_value)
        db.session.add(new_key)
        db.session.commit()
        flash("Anahtar başarıyla oluşturuldu!", "success")

    return render_template('generate.html')

# Keyleri Listeleme ve Bağlantı
@app.route('/connect')
@login_required
def connect():
    keys = Key.query.filter_by(user_id=current_user.id).all()
    return render_template('connect.html', keys=keys)

# Çıkış Yapma
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Çıkış yaptınız!", "info")
    return redirect(url_for('login'))

# Veritabanını oluşturma
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



