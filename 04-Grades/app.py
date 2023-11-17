# importowanie modułów i klas
from flask import Flask, render_template, session, redirect
from flask_bs4 import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import json
from flask_moment import Moment
from datetime import datetime
import requests

# konfiguracja aplikacji
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'FVGSBf7t28ub*#&$shhfbiaasd'
moment=Moment(app)
date = datetime.now()
class LoginForm(FlaskForm):
    '''login form'''
    userLogin = StringField('Nazwa użytkownika:', validators=[DataRequired()] )
    userPass = PasswordField('Hasło:', validators=[DataRequired()] )
    submit = SubmitField('Zaloguj')

class SubjectForm(FlaskForm):
    subject = StringField('Nazwa przedmiotu:', validators=[DataRequired()])
    submit = SubmitField('Dodaj')
def calculateAvg(grades, out_type=0):
    output = {}
    all_sum = 0
    all_iter = 0
    for subject, terms in grades.items():
        suma = 0
        iter = 0
        for cat, values in terms['term1'].items():
            if cat != "interim":
                if type(values) != list:
                    values = [values]
                for value in values:
                    suma+=value
                    iter+=1
        if iter != 0:
            term1avg = suma/iter
        else:
            term1avg = 0
        suma=0
        iter=0
        for cat, values in terms['term2'].items():
            if cat != "interim" and cat != "yearly":
                if type(values) != list:
                    values = [values]
                for value in values:
                    suma+=value
                    iter+=1
        if iter != 0:
            term2avg = suma/iter
        else:
            term2avg = 0
        if out_type == 0:
            output[subject] = [round(term1avg,2),round(term2avg,2),round((term1avg+term2avg)/2,2)]
        if out_type == 1:
            all_sum += round((term1avg+term2avg)/2,2)
            all_iter += 1
            output = all_sum/all_iter

    return output






# główna część aplikacji
@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['POST','GET'])
def login():
    with open('./data/users.json') as UsersFile:
        users = json.load(UsersFile)
        UsersFile.close()
    login = LoginForm()
    if login.validate_on_submit():
        userLogin = login.userLogin.data
        userPass = login.userPass.data
        if userLogin == users['userLogin'] and userPass == users['userPass']:
            session['userLogin'] = userLogin
            session['firstName'] = users['firstName']
            return redirect('dashboard')
    return render_template('login.html', title='Logowanie', login=login)

@app.route('/logout')
def logout():
    session.pop('userLogin')
    return redirect('/')

@app.route('/addSubject', methods=['POST','GET'])
def addSubject():
    addSubject = SubjectForm()
    if addSubject.validate_on_submit():
        with open('data/grades.json', encoding='utf-8') as gradesFile:
            grades = json.load(gradesFile)
            gradesFile.close()
            subject = addSubject.subject.data
            grades[subject]={
                "term1": {
                    "answer": [],
                    "quiz": [],
                    "test": [],
                    "interim": 1
                },
                "term2": {
                    "answer": [],
                    "quiz": [],
                    "test": [],
                    "interim": 1,
                    "yearly": 1
                }
            }
        with open('data/grades.json','w', encoding='utf-8') as gradesFile:
            json.dump(grades, gradesFile)
            gradesFile.close()
            redirect('/dashboard')

    return render_template('add-subject.html', title='Dodaj przedmiot', userLogin=session.get('userLogin'), firstName=session.get('firstName'), date=date, addSubject=addSubject)



@app.route('/dashboard')
def dashboard():
    with open('./data/grades.json') as file:
        grades = json.load(file)
        file.close()
    pogoda_src = requests.get("https://danepubliczne.imgw.pl/api/data/synop/id/12566")
    pogoda_krakow = json.loads(pogoda_src.content)
    return render_template('dashboard.html', title='Dashboard', userLogin=session.get('userLogin'), firstName=session.get('firstName'), date=date, grades=grades,calculateAvg = calculateAvg, pogoda=pogoda_krakow)

@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html', title='Nie ma takiej strony', firstName=session.get('firstName')), 404

@app.errorhandler(500)
def serverError(e):
    return render_template('500.html', title='Wewnętrzny błąd serwera', firstName=session.get('firstName')), 500

# uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)