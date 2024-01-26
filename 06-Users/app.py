# importowanie modułów i klas
import os

from flask import Flask, render_template, session, redirect, url_for
from flask_bs4 import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# konfiguracja aplikacji
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'FVGSBf7t28ub*#&$shhfbiaasd'

#konfig bazy danych
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data/users.sqlite')
db = SQLAlchemy(app)

#tabela bazy danych

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(20))
    lastName = db.Column(db.String(30))
    userMail = db.Column(db.String(50), unique=True)
    userPassword = db.Column(db.String(50))

    def is_authenticated(self):
        return True
#konfig Flask-login


#formularze
class LoginForm(FlaskForm):
    """Formularz logowania"""
    userMail = EmailField('Mail', validators=[DataRequired()], render_kw={'placeholder': 'Mail'})
    userPass = PasswordField('Hasło', validators=[DataRequired()], render_kw={'placeholder': 'Hasło'})
    submit = SubmitField('Zaloguj')

class RegisterForm(FlaskForm):
    """Formularz rejestracyjny"""
    firstName = StringField('Imię', validators=[DataRequired()], render_kw={'placeholder': 'Imię'})
    lastName = StringField('Nazwisko', validators=[DataRequired()], render_kw={'placeholder': 'Nazwisko'})
    userMail = EmailField('Mail', validators=[DataRequired()], render_kw={'placeholder': 'Mail'})
    userPass = PasswordField('Hasło', validators=[DataRequired()], render_kw={'placeholder': 'Hasło'})
    submit = SubmitField('Zarejestruj się!')

# główna część aplikacji
@app.route('/')
def index():
    return render_template('index.html', title='Home', headLine = "Zarządzanie użytkownikami")

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    return render_template('login.html', title='Logowanie', headLine="Logowanie", login_form=login_form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    return render_template('register.html', title='Logowanie', headLine="Logowanie", register_form=register_form)

# @app.errorhandler(404)
# def pageNotFound(e):
#     return render_template('404.html', title='Nie ma takiej strony', firstName=session.get('firstName')), 404
#
# @app.errorhandler(500)
# def serverError(e):
#     return render_template('500.html', title='Wewnętrzny błąd serwera', firstName=session.get('firstName')), 500

# uruchomienie aplikacji
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)