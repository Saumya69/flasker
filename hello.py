from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime


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

# create model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

# create string
    def __repr__(seif):
        return '<Name %r>' % self.name



# form class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
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
            name_to_update = name_to_update)





# def index():
#   return "<h1>hello world!</h1>"

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first() 
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
            name = form.name.data   
            form.name.data = ''
            form.email.data = ''
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
