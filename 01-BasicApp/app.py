# importowanie modułów i klas
from flask import Flask, render_template

# konfiguracja aplikacji
app = Flask(__name__)

# główna część aplikacji
@app.route('/')
def index():
    return '<h3>Hello Flask!!!</h3>'

@app.route('/template')
def template():
    return render_template('template.html', title='Template')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', title='User', userName=name)

# uruchomienie aplikacji
if __name__ == '__main__':
    app.run(debug=True)