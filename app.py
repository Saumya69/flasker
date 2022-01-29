from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin, login_user,LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm,PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os 


# flask instance
app = Flask(__name__)
# add ckeditor
ckeditor = CKEditor(app)
# add db
#old sqlite db
#new mysql db
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql:///username:@localhost/db_name'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://users.db'
app.config['SQLALCHEMY_DATABASE_URI'] ='postgres://ebzaecvcavoupr:678529d760f3ea8b8bcb3ed7fc529a41c0e625dc151e209914c836e1f00e6568@ec2-3-227-15-75.compute-1.amazonaws.com:5432/d8jlbsjlodv8kb'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ilovesaumyavbts9@localhost/our_users'
# secret key
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# intialize db
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#flasklogin stuffs
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#pass stuff to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

    #admin page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template("admin.html")
    else:
        flash("Sorry you must be the Admin to access the admin page !!")
        return redirect(url_for('dashboard'))
        



      

#create search func tion
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        #get data from submitted forms
        post.searched = form.searched.data
        #query db
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()


        return render_template("search.html",
         form=form, 
         searched = post.searched,
         posts = posts)



# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #check hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successful!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - try again !!")
        else:
            flash("That user do not exist-try again !!")

    return render_template('login.html',form=form)

#logout page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!!")
    return redirect(url_for('login'))

# dashboard page

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
     name_to_update.name = request.form['name'] 
     name_to_update.email = request.form['email']
     name_to_update.favorite_color = request.form['favorite_color']
     name_to_update.username = request.form['username']
     name_to_update.about_author = request.form['about_author']
     name_to_update.profilepic = request.files['profilepic']
    
     # grab imagename
     pic_filename = secure_filename(name_to_update.profilepic.filename)
     # set uuid
     pic_name = str(uuid.uuid1()) + "_" + pic_filename
     
     #save image
     saver = request.files['profilepic']
     

     #change it to a string to save to db
     name_to_update.profilepic = pic_name

     try:
        db.session.commit()
        saver.name_to_update.profilepic.save(os.path.join()(app.config['UPLOAD_FOLDER']), pic_name)
        flash("User Updated Successfully")
        return render_template("dashboard.html",
            form=form,
            name_to_update = name_to_update)
     except:
        flash("ERROR!! looks like there was a problem .....try again!!")
        return render_template("dashboard.html",
            form=form,
            name_to_update = name_to_update)
    else:
        return render_template("dashboard.html",
            form=form,
            name_to_update = name_to_update,
            id = id)

    return render_template('dashboard.html')



@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            #return msg
            flash("Blog Post Was Deleted")

            #grab all the posts from the db
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)


        except:
            # return an error msgg
            flash("OOPS!! There was a problem deleting post,try again !!")

            #grab all the posts from the db
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    
    else:
        #return msg
            flash("You are not authorized to delete that post")

            #grab all the posts from the db
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)



@app.route('/posts')
def posts():
#grab all the posts from the db
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html", posts=posts)

@app.route('/posts/<int:id>')
def  post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

@app.route('/posts/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
       # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # update db
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!!")
        return redirect(url_for('post',id=post.id))
    form.title.data = post.title
    #form.author.data = post.author 
    form.slug.data = post.slug
    form.content.data = post.content
    return render_template("edit_post.html", form=form)


# add post page
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id=poster, slug=form.slug.data)
        # clear forms
        form.title.data = ''
        form.content.data = ''
        #form.author.data = ''
        form.slug.data = ''

        #add post data to db
        db.session.add(post)
        db.session.commit() 

        #return msg
        flash("Blog Post Submitted Successfully!!")

    #redirect to the webpage
    return render_template("add_post.html", form=form)

# json thing
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "sana": "cheese",
        "riya": "butter"
    }
    return favorite_pizza
    return {"Date": date.today()}

#delete db
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!")


        our_users = Users.query.order_by(Users.date_added) 
        return render_template("add_user.html",
        form = form,
        name=name,
        our_users=our_users)


    except:
        flash("There was a problem deleting file.....")
        return render_template("add_user.html",
        form = form,
        name=name,
        our_users=our_users)


# update db records
@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
     name_to_update.name = request.form['name'] 
     name_to_update.email = request.form['email']
     name_to_update.favorite_color = request.form['favorite_color']
     name_to_update.username = request.form['username']

     try:
        db.session.commit()
        flash("User Updated Successfully")
        return render_template("update.html",
            form=form,
            name_to_update = name_to_update)
     except:
        flash("ERROR!! looks like there was a problem .....try again!!")
        return render_template("update.html",
            form=form,
            name_to_update = name_to_update)
    else:
        return render_template("update.html",
            form=form,
            name_to_update = name_to_update,
            id = id)

# def index():
#   return "<h1>hello world!</h1>"

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first() 
        if user is None:

            #hash pw
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")

            user = Users(username = form.username.data,name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            name = form.name.data   
            form.name.data = ''
            form.username.data = ''
            form.email.data = ''
            form.favorite_color = ''
            form.password_hash = ''

            flash("User Added Successfully")
    our_users = Users.query.order_by(Users.date_added)    
    return render_template("add_user.html",
        form = form,
        name=name,
        our_users=our_users)

# route decorator
@app.route('/')
def index():
        first_name = "Sana"
        stuff = "this is bold text"
        flash("Welcome To Our Website")
        favorite_pizza = ["Pepperoni", "Cheese", "mushrooms", 41]
        return render_template("index.html",
        first_name=first_name,
        stuff=stuff,
        favorite_pizza=favorite_pizza)

# localhost:5000/user/sana
@app.route('/user/<name>')

def user(name):
    return render_template("user.html" , user_name=name)
# create custom error page

#invalid urls
@app.errorhandler(404)
def page_mot_found(e):
    return render_template("404.html" ), 404

    #invalid urls
@app.errorhandler(500)
def page_mot_found(e):
    return render_template("500.html" ), 500


#  create pw test page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()


    # validate form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # to clear the forms
        form.email.data = ''
        form.password_hash.data = ''

        # lookup user by email address
        pw_to_check = Users.query.filter_by(email=email).first()

        # check hashed pw
        passed = check_password_hash(pw_to_check.password_hash, password)

        
       # flash("Form Submitted Successfully")

    return render_template("test_pw.html",
    email = email,
    password = password,
    pw_to_check = pw_to_check,
    passed = passed,
    form = form )


# name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # validate form
    if form.validate_on_submit():
        name = form.name.data 
        form.name.data = ''
        flash("Form Submitted Successfully")

    return render_template("name.html",
    name = name,
    form = form )


#create a blog post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    #author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

#foreign key to link users(refer to primary keyy)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))



# create model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100))
    about_author = db.Column(db.Text(), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profilepic = db.Column(db.String(300), nullable=True)
# do some pw stuff 
    password_hash = db.Column(db.String(100))
    #user can have many posts
    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
            raise AttributeError('password is not readable attribute 11')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create string
    def __repr__(seif):
        return '<Name %r>' % self.name
