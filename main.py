from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'y35235kssw2342e235'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(140), unique=True)
    password = db.Column(db.String(140))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/login', methods=['POST','GET'])
def login():
    username_error = ""
    password_error = ""

    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if user and password:
            session['username'] = username
            return redirect('/newpost')
        if not user:
            return render_template('login.html', username_error="Username does not exist.")
        else:
            return render_template('login.html', password_error="Your username or password was wrong.")

    return render_template('login.html')




@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('userid')
    posts = Blog.query.all()

    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template("post.html", title=post.title, body=post.body, user=post.owner.username, user_id=post.owner_id)
    if user_id:
        submissions = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('user.html', submissions=submissions)

    return render_template('blog.html',posts=posts)


@app.route('/newpost')
def post():
    return render_template('newpost.html', title="New Post")

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    title = request.form['title']
    body = request.form["body"]
    owner = User.query.filter_by(username=session['username']).first()

    title_error = ""
    body_error = ""

    if title == "":
        title_error = "Title required."
    if body == "":
        body_error = "Content required."

    if not title_error and not body_error:
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        page_id = new_post.id
        return redirect("/blog?id={0}".format(page_id))
    else:
        return render_template("newpost.html",
            title = title,
            body = body,
            title_error = title_error,
            body_error = body_error
        )

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        exist = User.query.filter_by(username=username).first()

        username_error = ""
        password_error = ""
        verify_error = ""

        if username == "":
            username_error = "Enter a username."
        elif len(username) <= 3 or len(username) > 20:
            username_error = "Username must be 3 and 20 characters long."
        elif " " in username:
            username_error = "Username cannot have any spaces."
        if password == "":
            password_error = "Please enter a password."
        elif len(password) <= 3:
            password_error = "Password must be more than 3 characters long."
        elif " " in password:
            password_error = "Password cannot have any spaces."
        if password != verify or verify == "":
            verify_error = "Passwords do not match."
        if exist:
            username_error = "Username is already taken."


        if len(username) > 3 and len(password) > 3 and password == verify and not exist:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html',
            username=username,
            username_error=username_error,
            password_error=password_error,
            verify_error=verify_error
            )

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()
