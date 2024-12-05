from flask import Flask, render_template, url_for, redirect, request, flash, abort
from flask_sqlalchemy import SQLAlchemy
from model import Artical, User, Chats, Msg, db
from flask_login import LoginManager, login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret-key-goes-here'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socketio = SocketIO(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/home')
def home():
    chats = Chats.query.order_by(Chats.date).all()
    articals = Artical.query.order_by(Artical.date).all()
    
    k=0
    for el in articals:
        if el.is_deleted == False:
            k += 1
    n=0
    for el in chats:
        if el.is_deleted == False:
            n += 1
    return render_template('main.html', user=current_user, chats=chats, articals=articals, k=k, n=n)

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

    timecheck = datetime.now().time()

    article.views += 1
    db.session.commit()

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

@app.route('/chats')
def chats():
    if current_user.is_authenticated != True:
        return redirect(url_for('login'))
    chats = Chats.query.order_by(Chats.date).all()
    k = 0
    for el in chats:
        if el.is_deleted == False:
            k += 1
    n = 0
    for el in chats:
        if (el.is_deleted == False and el.first_user_id == current_user.id):
            n += 1
    return render_template('chats.html', user=current_user, k=k, chats=chats, n=n)

@app.route('/new_chat', methods=['POST', 'GET'])
def new_chat():
    if current_user.is_authenticated != True:
        return redirect(url_for('login'))
    if request.method == "POST":
        
        img_src = request.form['src']
        title = request.form['title']
        description = request.form['discription']
        user_id = current_user.id
        user = current_user.username

        chat = Chats.query.filter_by(title = title).first()
        if (img_src == "" or title == "" or description == ""):
            flash('Некоторые поля не заполнены')
        else:
            if(chat):
                flash('Такой чат уже существует')
            else:
                if(len(description) > 100):
                    flash('Описание должно быть меньше 100 символов')
                else:
                    new_chat = Chats(img_src=img_src, title=title, description=description, first_user_id=user_id, first_user_name=user)
                    db.session.add(new_chat)
                    db.session.commit()
                    return redirect(url_for('chats'))
    return render_template('new_chat.html', user=current_user)

@app.route('/chat/<int:id>')
def chat(id):
    chat = Chats.query.get(id)
    if current_user.is_authenticated == False:
        return redirect(url_for('login'))

    return render_template('chat.html', user=current_user, chat=chat)

@app.route('/chat/<int:id>/changings', methods=['POST', 'GET'])
def chat_changings(id):
    chat = Chats.query.get(id)
    if current_user.is_authenticated == False:
        return redirect(url_for('login'))
    if current_user.id == chat.first_user_id:
        if request.method == "POST":
            img_src = request.form['src']
            title = request.form['title']
            description = request.form['description']

            if (img_src == "" or title == "" or description == ""):
                flash('Некоторые поля не заполнены')
            else:
                if (title == chat.title):
                    chat.title = title
                    chat.img_src = img_src
                    chat.description = description
                    db.session.commit()
                else:
                    chats = Chats.query.filter_by(title = title).first()

                    if (chats):
                        flash('Такой чат уже существует')
                    else:
                        chat.title = title
                        chat.img_src = img_src
                        chat.description = description
                        db.session.commit()
            return redirect(url_for('chats'))
    else: 
        abort(403)
    return render_template('chat_changings.html', user=current_user, chat=chat)


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

@app.route('/chat/<int:id>/delete_chat')
def delete_chat(id):
    chat = Chats.query.get(id)

    if current_user.is_authenticated == False:
        return redirect(url_for('login'))
    if current_user.id == chat.first_user_id:
        chat.is_deleted = True
        db.session.commit()
        logout_user()
        return redirect(url_for('home'))
    else:
        abort(403)

# @app.route('/test')
# def test():
#     return render_template('errors/402.html')

@app.errorhandler(400)
def bad_request(e):
    return render_template('errors/400.html'), 400

@app.errorhandler(401)
def unauthorized(e):
    return render_template('errors/401.html'), 401

# @app.errorhandler(402)
# def payment_required(e):
#     return render_template('errors/402.html'), 402

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(404)
def not_found_error(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('errors/405.html'), 405

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(501)
def not_implemented(e):
    return render_template('errors/501.html'), 501

@app.errorhandler(502)
def bad_gateway(e):
    return render_template('errors/502.html'), 502

@app.errorhandler(503)
def service_unavailable(e):
    return render_template('errors/503.html'), 503



@socketio.on('connect')
def connect_event(data):
    print('Client connected')

@socketio.on('message')
def handle_message(data):
    if data == '':
        flash('Вы не можете отправить пустую строку')
    else:
        print('This is a message:', data)

@socketio.on('new event')
def handle_new_event(data):
    print('A new event was emitted from the client containing the following payload', data)
    socketio.emit('server event', {'data': 'This is how you trigger a custom event from the server-side'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')