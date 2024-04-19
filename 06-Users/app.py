# importowanie modułów i klas
import os

from flask import Flask, render_template, session, redirect, url_for, flash, request, abort
from flask_bs4 import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, SelectField, FileField, HiddenField
from wtforms.validators import DataRequired, Length
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename
from datetime import datetime


# konfiguracja aplikacji
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'FVGSBf7t28ub*#&$shhfbiaasd'
app.config['UPLOAD_PATH'] = 'uploads'
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.jpeg', '.png', '.txt']
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
bcrypt = Bcrypt(app)

#lokalizacja uzytkownika w strukturze danych
userLocation = ''

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
    userRole = db.Column(db.String(50))

class Folders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    folderName = db.Column(db.String(50),unique=True)
    type = db.Column(db.String(20))
    icon = db.Column(db.String(40))
    time = db.Column(db.String(20))
    path = db.Column(db.String(500))

class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fileName = db.Column(db.String(50), unique=True)
    type = db.Column(db.String(20))
    icon = db.Column(db.String(40))
    time = db.Column(db.String(20))
    size = db.Column(db.String(20))
    path = db.Column(db.String(500))

    def is_authenticated(self):
        return True
#konfig Flask-login
loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'
loginManager.login_message = 'Nie jesteś zalogowany!'
loginManager.login_message_category = 'warning'

@loginManager.user_loader
def loadUser(id):
    return Users.query.filter_by(id=id).first()


#formularze
class LoginForm(FlaskForm):
    """Formularz logowania"""
    userMail = EmailField('Mail', validators=[DataRequired()], render_kw={'placeholder': 'Mail'})
    userPass = PasswordField('Hasło', validators=[DataRequired()], render_kw={'placeholder': 'Hasło'})
    submit = SubmitField('Zaloguj')

class chPasswdForm(FlaskForm):
    """Formularz zmiany hasła"""
    oldUserPass = PasswordField('stare hasło', validators=[DataRequired()], render_kw={'placeholder': 'stare hasło'})
    newUserPass = PasswordField('nowe hasło', validators=[DataRequired()], render_kw={'placeholder': 'Hasło'})
    submit = SubmitField('Zmień hasło')

class SudoChPasswdForm(FlaskForm):
    """Formularz zmiany hasła przez administratora"""
    newUserPass = PasswordField('nowe hasło', validators=[DataRequired()], render_kw={'placeholder': 'Hasło'})
    submit = SubmitField('Zmień hasło')

class RegisterForm(FlaskForm):
    """Formularz rejestracyjny"""
    firstName = StringField('Imię', validators=[DataRequired()], render_kw={'placeholder': 'Imię'})
    lastName = StringField('Nazwisko', validators=[DataRequired()], render_kw={'placeholder': 'Nazwisko'})
    userMail = EmailField('Mail', validators=[DataRequired()], render_kw={'placeholder': 'Mail'})
    userPass = PasswordField('Hasło', validators=[DataRequired()], render_kw={'placeholder': 'Hasło'})
    submit = SubmitField('Zarejestruj się!')

class EditUserForm(FlaskForm):
    """Formularz edycji użytkownika"""
    firstName = StringField('Imię', validators=[DataRequired()], render_kw={'placeholder': 'Imię'})
    lastName = StringField('Nazwisko', validators=[DataRequired()], render_kw={'placeholder': 'Nazwisko'})
    userMail = EmailField('Mail', validators=[DataRequired()], render_kw={'placeholder': 'Mail'})
    userRole = SelectField('Uprawnienia', validators=[DataRequired()], choices=[('user','Użytkownik'),('admin', 'Administrator')])
    submit = SubmitField('Zarejestruj się!')

class AddUserForm(FlaskForm):
    """Formularz dodawania użytkownika przez administratora"""
    firstName = StringField('Imię', validators=[DataRequired()], render_kw={'placeholder': 'Imię'})
    lastName = StringField('Nazwisko', validators=[DataRequired()], render_kw={'placeholder': 'Nazwisko'})
    userMail = EmailField('Mail', validators=[DataRequired()], render_kw={'placeholder': 'Mail'})
    userPass = PasswordField('Hasło', validators=[DataRequired()], render_kw={'placeholder': 'Hasło'})
    userRole = SelectField('Uprawnienia', validators=[DataRequired()], choices=[('user','Użytkownik'),('admin', 'Administrator')])

    submit = SubmitField('Zarejestruj się!')

class SearchForm(FlaskForm):
    """Formularz edycji użytkownika"""
    SearchKey = StringField('Szukaj', validators=[DataRequired()])
    submit = SubmitField('Szukaj')

class CreateFolder(FlaskForm):
    """Formularz edycji użytkownika"""
    name = StringField('NazwaFolderu', validators=[DataRequired()], render_kw={'placeholder': 'Nowy Folder'})
    submit = SubmitField('Dodaj')

class UploadFiles(FlaskForm):
    """formularz do przesyłania pliku"""
    fileName = FileField('Nazwa pliku', validators=[FileAllowed(app.config['UPLOAD_EXTENSIONS'])])
    submit = SubmitField('Prześlij')

class RenameFolder(FlaskForm):
    """formularz zmiany nazwy folderu"""
    folderName = StringField('Nowa nazwa folderu', validators=[DataRequired()], render_kw={'placeholder': 'Nowa Nazwa'})
    submit = SubmitField('Zapisz')

# główna część aplikacji
@app.route('/')
def index():
    return render_template('index.html', title='Home', headLine = "Zarządzanie użytkownikami")

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = Users.query.all()
    if not user:
        return redirect(url_for('register'))
    else:
        login_form = LoginForm()
        if login_form.validate_on_submit():
            user = Users.query.filter_by(userMail=login_form.userMail.data).first()
            if user:
                if bcrypt.check_password_hash(user.userPassword, login_form.userPass.data):
                    login_user(user)
                    return redirect(url_for('dashboard'))
    return render_template('login.html', title='Logowanie', headLine="Logowanie", login_form=login_form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    register_form = RegisterForm()
    users = Users.query.all()
    if register_form.validate_on_submit() and not users:
        try:
            hashed_password = bcrypt.generate_password_hash(register_form.userPass.data)
            newUser = Users(userMail=register_form.userMail.data, userPassword=hashed_password, firstName=register_form.firstName.data, lastName = register_form.lastName.data, userRole="admin")
            db.session.add(newUser)
            db.session.commit()
            flash('Konto utworzone poprawnie', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Taki adres E-Mail już istnieje!', 'danger')
            return redirect(url_for('register'))
    elif register_form.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(register_form.userPass.data)
            newUser = Users(userMail=register_form.userMail.data, userPassword=hashed_password, firstName=register_form.firstName.data, lastName = register_form.lastName.data, userRole="user")
            db.session.add(newUser)
            db.session.commit()
            time = datetime.now().strftime('%Y%m%d %H:%M:%S')
            newFolder = Folders(folderName=register_form.firstName.data, type="folder", icon="bi bi-folder", time=time, path='/')
            os.mkdir(os.path.join(app.config['UPLOAD_PATH'], register_form.firstName.data))
            db.session.add(newFolder)
            db.session.commit()
            flash('Konto utworzone poprawnie', 'success')
            flash('Konto utworzone poprawnie', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Taki adres E-Mail już istnieje!', 'danger')
            return redirect(url_for('register'))
    return render_template('register.html', title='Logowanie', headLine="Logowanie", register_form=register_form)

@app.route('/addUser', methods=['GET', 'POST'])
@login_required
def addUser():
    addForm = AddUserForm()
    if addForm.validate_on_submit():
        try:
            hashed_password = bcrypt.generate_password_hash(addForm.userPass.data)
            newUser = Users(userMail=addForm.userMail.data, userPassword=hashed_password, firstName=addForm.firstName.data, lastName = addForm.lastName.data, userRole = addForm.userRole.data )
            db.session.add(newUser)
            db.session.commit()
            time = datetime.now().strftime('%Y%m%d %H:%M:%S')
            newFolder = Folders(folderName=addForm.firstName.data, type="folder", icon="bi bi-folder", time=time, path='/')
            os.mkdir(os.path.join(app.config['UPLOAD_PATH'], addForm.firstName.data))
            db.session.add(newFolder)
            db.session.commit()
            flash('Konto utworzone poprawnie', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Taki adres E-Mail już istnieje!', 'danger')
            return redirect(url_for('dashboard'))
    return render_template('register.html', title='Logowanie', headLine="Logowanie", register_form=addForm)

@app.route('/deleteUser', methods=['GET', 'POST'])
@login_required
def deleteUser():
    if request.method == 'GET':
        id = request.args.get('id')
        user = Users.query.filter_by(id=id).one()
        db.session.delete(user)
        db.session.commit()
        flash('Użytkownik usunięty poprawnie', 'success')
        return redirect(url_for('dashboard'))

@app.route('/editUser<int:id>', methods=['GET', 'POST'])
@login_required
def editUser(id):
    editUser = EditUserForm()
    user = Users.query.get_or_404(id)
    if editUser.validate_on_submit():
        try:
            user.firstName = editUser.firstName.data
            user.lastName = editUser.lastName.data
            user.userMail = editUser.userMail.data
            user.userRole = editUser.userRole.data
            db.session.commit()
            flash('Dane użytkownika zostały zmienione!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            print(e)

@app.route('/changePassword', methods=['GET', 'POST'])
@login_required
def chPasswd():
    chPasswd = chPasswdForm()
    user = Users.query.get_or_404(current_user.id)
    if chPasswd.validate_on_submit():
        try:
            if bcrypt.check_password_hash(user.userPassword, chPasswd.oldUserPass.data):
                hashed_password = bcrypt.generate_password_hash(chPasswd.newUserPass.data)
                user.userPassword = hashed_password
                db.session.commit()
                flash('Hasło zmienione!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Złe hasło!', 'danger')
                return redirect(url_for('dashboard'))
        except Exception as e:
            print(e)
            flash('Błąd!', 'danger')
            return redirect(url_for('dashboard'))

@app.route('/userPasswd<int:id>', methods=['GET', 'POST'])
@login_required
def ChUserPasswd(id):
    chPasswd = SudoChPasswdForm()
    user = Users.query.get_or_404(id)
    if chPasswd.validate_on_submit():
        try:
             hashed_password = bcrypt.generate_password_hash(chPasswd.newUserPass.data)
             user.userPassword = hashed_password
             db.session.commit()
             flash('Hasło zmienione!', 'success')
             return redirect(url_for('dashboard'))
        except Exception as e:
            print(e)
            flash('Błąd!', 'danger')
            return redirect(url_for('dashboard'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/createFolder', methods=['GET', 'POST'])
@login_required
def createFolder():
   folderName = request.form['name']
   if folderName != '':
       time = datetime.now().strftime('%Y%m%d %H:%M:%S')
       newFolder = Folders(folderName = folderName, type="folder", icon="bi bi-folder", time=time, path=userLocation)
       print(os.path.join(app.config['UPLOAD_PATH'], current_user.firstName, userLocation ,folderName))
       os.mkdir(os.path.join(app.config['UPLOAD_PATH'], current_user.firstName, userLocation, folderName))
       db.session.add(newFolder)
       db.session.commit()
       flash('Folder utworzony poprawnie', 'success')
   return redirect(url_for('dashboard'))

@app.route('/uploadFile', methods=['GET', 'POST'])
@login_required
def uploadFile():
    uploadedFile = request.files['fileName']
    fileName = secure_filename(uploadedFile.filename)
    if fileName != '':
        fileExtension = os.path.splitext(fileName)[1]
        if fileExtension not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        type = ''
        icon = ''
        if fileExtension == '.png':
            type = 'png'
            icon = 'bi bi-filetype-png'
        elif fileExtension == '.jpg':
            type = 'jpg'
            icon = 'bi bi-filetype-jpg'
        elif fileExtension == '.jpeg':
            type = 'jpeg'
            icon = 'bi bi-filetype-jpg'
        elif fileExtension == '.txt':
            type = 'txt'
            icon = 'bi bi-filetype-txt'
        uploadedFile.save(os.path.join(app.config['UPLOAD_PATH'], current_user.firstName, userLocation, fileName))
        size = round(os.stat(os.path.join(app.config['UPLOAD_PATH'], current_user.firstName, userLocation, fileName)).st_size / (1024 * 1024), 2)
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        newFile = Files(fileName=fileName, type=type, icon=icon, time=time, size=size, path=userLocation)
        db.session.add(newFile)
        db.session.commit()
        flash('Plik przesłany poprawnie', 'success')
        return redirect(url_for('dashboard'))

@app.route('/renameFolder', methods=('GET', 'POST'))
@login_required
def renameFolder():
    id = request.form['folderId']
    newName = request.form['folderName']
    if newName != '':
        folder = Folders.query.get_or_404(id)
        os.rename(os.path.join(app.config['UPLOAD_PATH'], folder.folderName), os.path.join(app.config['UPLOAD_PATH'], newName))
        folder.folderName = newName
        db.session.commit()
        flash('Zmiana nazwy folderu udana!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/deleteFolder', methods=('GET', 'POST'))
@login_required
def deleteFolder():
    id = request.form['folderId']
    folder = Folders.query.get_or_404(id)
    os.rmdir(os.path.join(app.config['UPLOAD_PATH'], folder.folderName))
    db.session.delete(folder)
    db.session.commit()
    flash('Folder usunięty poprawnie!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/renameFile', methods=('GET', 'POST'))
@login_required
def renameFile():
    id = request.form['fileId']
    oldName = request.form['oldName']
    extension = oldName.split('.')[-1]
    newName = request.form['folderName']
    if newName != '':
        if '.' not in newName:
            newName = newName + '.' + extension
        file = Files.query.get_or_404(id)
        os.rename(os.path.join(app.config['UPLOAD_PATH'], file.fileName), os.path.join(app.config['UPLOAD_PATH'], newName))
        file.fileName = newName
        db.session.commit()
        flash('Zmiana nazwy folderu udana!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/deleteFile', methods=('GET', 'POST'))
@login_required
def deleteFile():
    id = request.form['fileId']
    file = Files.query.get_or_404(id)
    os.remove(os.path.join(app.config['UPLOAD_PATH'], file.fileName))
    db.session.delete(file)
    db.session.commit()
    flash('Folder usunięty poprawnie!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    userLocation=""
    if request.args.get('path') != None:
        userLocation = request.args.get('path')
    folders = Folders.query.filter_by(path=userLocation).all()
    files = Files.query.filter_by(path=userLocation).all()
    users = Users.query.all()
    addUser = RegisterForm()
    editUser = RegisterForm()
    SudoChUserPassword = SudoChPasswdForm()
    chPasswd = chPasswdForm()
    search = SearchForm()
    createFolder = CreateFolder()
    uploadFiles = UploadFiles()
    renameFolder = RenameFolder()
    return render_template('dashboard.html', title='Dashboard', users=users, addUser=addUser,
    uploadFiles=uploadFiles,createFolder=createFolder,editUser=editUser, chPasswd=chPasswd,
    SudoChUserPassword=SudoChUserPassword, search=search, folders=folders, files=files, renameFolder=renameFolder)

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