from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import datetime
import pytz
import hashlib
import secrets


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///textter.db'
db = SQLAlchemy(app)

def hash_password(password:str)->str:
    return hashlib.sha256(password.encode()).hexdigest()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    text = db.Column(db.String(280), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    
    def __repr__(self):
        return '<Tweet %r>' % self.username


@app.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        tweet = request.form['tweet']
        tweet = Tweet(username=session['username'], text=tweet)
        db.session.add(tweet)
        db.session.commit()
        
    tweets = Tweet.query.filter_by(username=session['username']).all()
    return render_template('home.html', tweets=tweets)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        password_hash = hash_password(password)
        user = User(username=username, password=password_hash)
        db.session.add(user)
        db.session.commit()

        return redirect('/login')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hash_password(password)
        user = User.query.filter_by(username=username).first()
        if user:
            if password_hash == user.password:
                session['username'] = username
                return redirect('/home')
            else:
                return redirect('/')
        else:
            return redirect('/')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


@app.route('/tweet', methods=['POST'])
def tweet():
    if 'username' not in session:
        return redirect('/login')
    tweet = request.form['tweet']
    jst = pytz.timezone('Asia/Tokyo')
    tweet = Tweet(username=session['username'], text=tweet, created_at=datetime.datetime.now(jst))
    db.session.add(tweet)
    db.session.commit()
    return redirect('/home')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.secret_key = secrets.token_urlsafe(32)
    app.run()
