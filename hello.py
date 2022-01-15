from flask import Flask, render_template


# flask instance
app = Flask(__name__)

# route decorator
@app.route('/')

# def index():
#	return "<h1>hello world!</h1>"

def index():
	first_name = "Sana"
	stuff = "this is bold text"

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