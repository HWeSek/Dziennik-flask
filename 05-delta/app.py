# importowanie modułów i klas
from flask import Flask, render_template, session, redirect
from flask_bs4 import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField
from wtforms.validators import InputRequired
from math import sqrt


# konfiguracja aplikacji
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'FVGSBf7t28ub*#&$shhfbiaasd'

class inputForm(FlaskForm):
    '''login form'''
    parameterA = FloatField('a:', validators=[InputRequired()] )
    parameterB = FloatField('b:', validators=[InputRequired()] )
    parameterC = FloatField('c:', validators=[InputRequired()] )
    submit = SubmitField('Oblicz')


# główna część aplikacji
@app.route('/', methods=['POST','GET'])
def index():
    calculate = inputForm()
    if calculate.validate_on_submit():
        a = calculate.parameterA.data
        b = calculate.parameterB.data
        c = calculate.parameterC.data



        delta = b**2 - 4*a*c
        print(a,b,c)
        print(delta)
        x_i = 0
        x_ii = 0
        if delta > 0:
            if a == 0:
                print('error dzielenie przez 0')
            else:
             x_i = round((-b-sqrt(delta))/(2*a),2)
             x_ii = round((-b+sqrt(delta))/(2*a),2)
        elif delta == 0:
            if a == 0:
                print('error dzielenie przez 0')
            else:
             x_i = round(-b/2*a,2)
             x_ii=0
        elif delta < 0:
             print('brak rozwiązań')
        print(x_ii,x_i)
        return render_template('index.html', title='Liczenie delty', calculate=calculate, delta=delta, x_i=x_i,x_ii=x_ii)
    return render_template('index.html', title='Liczenie delty', calculate=calculate)


@app.errorhandler(404)
def pageNotFound(e):
    return render_template('404.html', title='Nie ma takiej strony'), 404

@app.errorhandler(500)
def serverError(e):
    return render_template('500.html', title='Wewnętrzny błąd serwera'), 500

# uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)