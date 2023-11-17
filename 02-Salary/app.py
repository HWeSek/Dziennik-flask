# importowanie modułów i klas
import json

from flask import Flask, render_template, session, redirect
from flask_bs4 import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


# konfiguracja aplikacji
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'FVGSBf7t28ub*#&$shhfbiaasd'

def SalaryExtremes(salaries):
    max = 0
    min = 99999999999999999
    for key, value in salaries.items():
        if int(value.split(';')[3]) > max:
            max = int(value.split(';')[3])
        if int(value.split(';')[3]) < min:
            min = int(value.split(';')[3])
    return [min, max]

def CalculateAvg(salaries):
    sum = 0
    intiger=0
    for key, value in salaries.items():
        sum += int(value.split(';')[3])
        intiger +=1
    return sum/intiger

class filterForm(FlaskForm):
    surname = StringField('Search with surname: ', validators=[DataRequired()])
    submit = SubmitField('Search')

# główna część aplikacji
@app.route('/', methods=['POST','GET'])
def index():
    with open('data/salary.json') as File:
        salaries = json.load(File)
        File.close()
    form = filterForm()
    if form.validate_on_submit():
        surname = form.surname.data
        return render_template('index.html', title='Home', salaries=salaries, minmax=SalaryExtremes(salaries),average=round(CalculateAvg(salaries), 2), form=form, surname=surname)

    return render_template('index.html', title='Home', salaries=salaries, minmax = SalaryExtremes(salaries), average=round(CalculateAvg(salaries),2), form=form)


@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html', title='Nie ma takiej strony'), 404

@app.errorhandler(500)
def serverError(e):
    return render_template('500.html', title='Wewnętrzny błąd serwera'), 500

# uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)