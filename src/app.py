from flask import Flask, render_template, url_for, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from model import Artical, User, db
from flask_login import LoginManager, login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret-key-goes-here'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/home')
def home():
    return render_template('main.html', user=current_user)

@app.route('/recomendation')
def recomendation():
    return render_template('recomendation.html', user=current_user)

@app.route('/subs')
def subs():
    return render_template('subs.html', user=current_user)

@app.route('/views')
def views():
        articals = Artical.query.order_by(Artical.date).all()
        k = 0
        for el in articals:
            if el.is_deleted == False:
                k += 1
        return render_template('views.html', user=current_user, k=k, articals=articals)

@app.route('/views/<int:id>', methods=['POST', 'GET'])
def view(id):
    article = Artical.query.get(id)

    if request.method == "POST":
        article.is_deleted = True
        db.session.commit()
        return redirect(url_for('views'))
    return render_template('view.html', user=current_user, article=article)

@app.route('/new_view', methods=['POST', 'GET'])
def new_view():
    if current_user.is_authenticated:
        if request.method == "POST":
            user = current_user.name
            user_id = current_user.id
            title = request.form['title']
            discription = request.form['discription']

            if (title == "" or discription == ""):
                flash("Нужно заполнить все поля")
            else:
                if (len(discription) < 2500 and len(discription) > 200):
                    new_artical = Artical(user_id=user_id, user=user, title=title, text=discription)
                    db.session.add(new_artical)
                    db.session.commit()
                    return redirect(url_for('views'))
                else:
                    flash("Ваш отзыв должен быть больше 200 символов и меньше 2500 символов ")
        return render_template('new_view.html', user=current_user)
    else:
        return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if current_user.is_authenticated:
        return render_template('profile.html', user=current_user)
    else:
        return redirect(url_for('login'))
    
@app.route('/changings', methods=['POST', 'GET'])
def changings():
    if current_user.is_authenticated != True:
        return render_template('login.html', user=current_user)

    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        phone_number = request.form['phone_number']
        password = request.form['password']
        password_chek = request.form['password_chek']
        name = request.form['name']
        second_name = request.form['second_name']
        age = request.form['age']
        town = request.form['town']

        user_change = User.query.filter_by(username = current_user.username).first()

        if (username == "" or email == "" or name == "" or age == None):
            flash('Обязательные поля не заполнены')
        else:
                if (len(name) > 14):
                    flash('Имя должно быть меньше 14 символов')
                else:
                    if (password != ""):
                        if (password_chek == ""):
                            flash('Новый пароль не записан')
                        else:
                            if (check_password_hash(current_user.password, password)):
                                user_change.username  = username
                                user_change.email = email
                                user_change.password = generate_password_hash(password_chek)
                                user_change.phone_number = phone_number
                                try:
                                    if phone_number != "":
                                        phone_number = int(phone_number)
                                        if phone_number > 0:
                                            user_change.phone_number = phone_number
                                        else:
                                            flash('Недопустимый номер телефона')
                                    user_change.name = name
                                    user_change.second_name = second_name
                                    try:
                                        user_change.age = int(age)
                                        if age > 0 and age < 122:
                                            user_change.town = town
                                            db.session.commit()
                                            return redirect(url_for('profile'))
                                        else:
                                            flash('Недопустимый возраст')
                                    except:
                                        flash('Вы заполнили строку возраста неправильно')
                                except:
                                    flash('Вы заполнили строку номера телефона неправильно')
                            else:
                                flash('Вы ввели неправильный пароль')
                    else:
                        user_change.username  = username
                        user_change.email = email
                        user_change.phone_number = phone_number
                        try:
                            if (phone_number != ""):
                                phone_number = int(phone_number)
                                if phone_number > 0:
                                    user_change.phone_number = phone_number
                                else:
                                    flash('Недопустимый номер телефона')
                            user_change.name = name
                            user_change.second_name = second_name
                            try:
                                age = int(age)
                                if age > 0 and age < 122:
                                    user_change.age = age
                                    user_change.town = town
                                    db.session.commit()
                                    return redirect(url_for('profile'))
                                else:
                                    flash('Недопустимый возраст')
                            except:
                                flash('Вы заполнили строку возраста неправильно')
                        except:
                            flash('Вы заполнили строку номера телефона неправильно')
    return render_template('changings.html', user=current_user)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if (username == "" or password == ""):
            flash('Некоторые поля не заполнены')
        else:
            if (user and check_password_hash(user.password ,password) and user.is_deleted == False):
                login_user(user)
                return redirect(url_for('profile'))
            else:
                flash('Неправильный логин, почта или пароль')
    return render_template('login.html')

@app.route('/create_acc', methods=['POST', 'GET'])
def create_acc():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']
        try:
            age = request.form['age']
            age = int(age)
            
            user = User.query.filter_by(username=username).first()

            if (username == "" or password == "" or email == "" or name == "" or age == None):
                flash('Некоторые поля не заполнены')
            else:
                if (user):
                    flash('Такой аккаунт уже существует')
                else:
                    if (len(name) > 14):
                        flash('Имя должно быть меньше 14 символов')
                    else:
                        if age > 0 and age < 122:
                            new_user = User(username=username, password=generate_password_hash(password), email=email, name=name, second_name="", town="", age=age, phone_number="")
                            db.session.add(new_user)
                            db.session.commit()
                            return redirect(url_for('login'))
                        else:
                            flash('Недопустимый возраст')
        except:
            flash('Вы заполнили строку возраста неправильно')
    return render_template("create_acc.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/delete')
def delete():
    user = current_user
    user.is_deleted = True
    db.session.commit()
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')