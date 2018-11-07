from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'y35235ksswe235'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1048))
    

    def __init__(self, title, body):
        self.title = title
        self.body = body
        
    
@app.route('/newpost', methods=['POST','GET'])
def newpost():
    body = ''
    heading = ''
    body_err = ''
    heading_err = ''

    if request.method == 'POST':
        heading = request.form['heading']
        body = request.form['text']

        if not empty_input(heading):
            heading_err = "Please input a title"

        if not empty_input(body):
            body_err = "Please input a body for the blog"

        new_blog = Blog(heading, body)
        db.session.add(new_blog)
        db.session.commit()
        new_id = new_blog.id
        if (not heading_err) and (not body_err):
            return redirect('/blog?id={0}'.format(new_id))


    return render_template('newpost.html', title='Build-A-Blog', body=body,heading=heading,body_err=body_err,heading_err=heading_err)



@app.route('/blog', methods=['POST','GET'])
def blog():

    blogs = Blog.query.all()
    if 'id' in request.args:
        my_id = request.args.get('id')
        my_page = Blog.query.filter_by(id=my_id).first()
        return render_template('individual.html', post=my_page)


    return render_template('blog.html', title="Build-A-Blog", blogs=blogs)



@app.route('/individual/<id>', methods=['PULL'])
def single_blog(id):
    
    return render_template('individual.html', title="Build-A-Blog")

@app.route('/', methods=['POST', 'GET'])
def index():

    
    blogs = Blog.query.all()
    

    return render_template('base.html', title="Build-A-Blog", blogs=blogs)

def empty_input(x):
    if x:
        return True
    else:
        return False



if __name__ == '__main__':
    app.run()
