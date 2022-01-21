from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

# flask instance
app = Flask(__name__)
# add db
#old sqlite db
#new mysql db
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql:///username:@localhost/db_name'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ilovesaumyavbts9@localhost/our_users'
# secret key!
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"

# intialize db
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# json thing
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "sana": "cheese",
        "riya": "butter"
    }
    return favorite_pizza
    return {"Date": date.today()}





# create model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    favorite_color = db.Column(db.String(100))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
# do some pw stuff 
    password_hash = db.Column(db.String(100))


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




# form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField('Password', validators=[DataRequired(), EqualTo('password_hash2', message = 'Passwords Must Match!!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = StringField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# form class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# update db records
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
     name_to_update.name = request.form['name'] 
     name_to_update.email = request.form['email']
     name_to_update.favorite_color = request.form['favorite_color']
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

            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
            name = form.name.data   
            form.name.data = ''
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
