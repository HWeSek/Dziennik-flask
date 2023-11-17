# importowanie modułów i klas
from flask import Flask, render_template, session, redirect
from flask_bs4 import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


# konfiguracja aplikacji
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'FVGSBf7t28ub*#&$shhfbiaasd'

class LoginForm(FlaskForm):
    '''login form'''
    userLogin = StringField('Nazwa użytkownika:', validators=[DataRequired()] )
    userPass = PasswordField('Hasło:', validators=[DataRequired()] )
    submit = SubmitField('Zaloguj')

users = {
    'userLogin': 'AC',
    'userPass': 'fumo',
    'firstName': 'Adam',
    'lastName': 'Cichon'
}


# główna część aplikacji
@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['POST','GET'])
def login():
    login = LoginForm()
    if login.validate_on_submit():
        userLogin = login.userLogin.data
        userPass = login.userPass.data
        if userLogin == users['userLogin'] and userPass == users['userPass']:
            session['userLogin'] = userLogin
            return redirect('dashboard')
    return render_template('login.html', title='Logowanie', login=login)

@app.route('/logout')
def logout():
    session.pop('userLogin')
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', title='Dashboard', userLogin=session.get('userLogin'))

@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html', title='Nie ma takiej strony'), 404

@app.errorhandler(500)
def serverError(e):
    return render_template('500.html', title='Wewnętrzny błąd serwera'), 500

# uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)