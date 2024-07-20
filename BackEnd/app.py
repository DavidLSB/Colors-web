from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import psycopg2


MAX_CHARACTERS_STRING = 40 #The max characters of a string in the database
RELATED_COLORS_MAX_AMOUNT = 5 #The max number of related colors of max length
DB_HOST = "localhost" #The database host
DB_NAME = "colorsdb" #The database name
DB_USER = "postgres" #The database username
DB_PASSWORD = "password" #The database password
TEMPLATE_FOLDER = '../FrontEnd' #The folder where the front-end folders are (the htmls)

app = Flask(__name__, template_folder = TEMPLATE_FOLDER)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME
app.app_context().push()
db = SQLAlchemy(app)


class Color(db.Model):
	__tablename__ = 'colors'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(MAX_CHARACTERS_STRING))
	color_temperature = db.Column(db.Integer)
	complementary_colors = db.Column(db.String(MAX_CHARACTERS_STRING*RELATED_COLORS_MAX_AMOUNT))
	analogous_colors = db.Column(db.String(MAX_CHARACTERS_STRING*RELATED_COLORS_MAX_AMOUNT))
	recipee_colors = db.Column(db.String(MAX_CHARACTERS_STRING*RELATED_COLORS_MAX_AMOUNT))
	
	def __init__(self, name, color_temperature, complementary_colors, analogous_colors, recipee_colors):
		self.name = name
		self.color_temperature = color_temperature
		self.complementary_colors = complementary_colors
		self.analogous_colors = analogous_colors
		self.recipee_colors = recipee_colors

class RGBValues(db.Model):
	__tablename__ = 'rgb_values'
	id = db.Column(db.Integer, primary_key=True)
	red = db.Column(db.Integer)
	green = db.Column(db.Integer)
	blue = db.Column(db.Integer)
	
	def __init__(self, red, green, blue):
		self.red = red
		self.green = green
		self.blue = blue

#Given a immutabledict object ("form"), creates a color class object, and a rgbvalues class object, and returns them in that order.
def create_color(form):
	name = form['name']
	color_temperature = form['color_temperature']
	complementary_colors = form['complementary_colors']
	analogous_colors = form['analogous_colors']
	recipee_colors = form['recipee_colors']
	red = form['red']
	green = form['green']
	blue = form['blue']
	color = Color(name, color_temperature, complementary_colors, analogous_colors, recipee_colors)
	rgbvalues = RGBValues(red, green, blue)
	return color, rgbvalues

#Given both a color class object and a rgbvalues class object, adds them to the database (POST)
def push_color(color, rgbvalues):
	db.session.add(color)
	db.session.add(rgbvalues)
	db.session.commit()

#Combination of both create_color and push_color, given an immutabledict object ("form"), creates all the necessary objects to push them the information of the form into the database
def create_color_and_push(form):
	color, rgbvalues = create_color(form)
	push_color(color, rgbvalues)

#Creates and pushes a color whose only known parametters are its RGB values (from the color mixer)
def create_unknown_color(request):
	form = request.dict_storage_class([
		("name", "Unknown"),
		("color_temperature", "3"),
		("complementary_colors", ""),
		("analogous_colors", ""),
		("recipee_colors", ""),
		("red", request.form['current_color_r']),
		("green", request.form['current_color_g']),
		("blue", request.form['current_color_b']),
	])
	
	create_color_and_push(form)

#Given an inmutabledict ("form") and the id of a color, updates it value on the database
def update_color(form, id):
	name = form['name']
	color_temperature = form['color_temperature']
	complementary_colors = form['complementary_colors']
	analogous_colors = form['analogous_colors']
	recipee_colors = form['recipee_colors']
	red = form['red']
	green = form['green']
	blue = form['blue']
	
	conn = psycopg2.connect(dbname = DB_NAME, user = DB_USER, password = DB_PASSWORD, host = DB_HOST)
	cur = conn.cursor()
	cur.execute("""
		UPDATE colors
		SET name = %s, color_temperature = %s, complementary_colors = %s, analogous_colors = %s, recipee_colors = %s
		WHERE id = %s
		""", (name, str(color_temperature), complementary_colors, analogous_colors, recipee_colors, str(id)))
	conn.commit()
	cur.execute("""
		UPDATE rgb_values
		SET red = %s, green = %s, blue = %s
		WHERE id = %s
		""", (str(red), str(green), str(blue), str(id)))
	conn.commit()
	cur.close()
	conn.close()

#Returns a list with all colors from the database
def get_colors_list():
	conn = psycopg2.connect(dbname = DB_NAME, user = DB_USER, password = DB_PASSWORD, host = DB_HOST)
	cur = conn.cursor()
	cur.execute('SELECT * FROM colors')
	colors_list = cur.fetchall()
	cur.close()
	conn.close()
	return colors_list

#Returns a list with all rgb_values from the database
def get_rgbvalues_list():
	conn = psycopg2.connect(dbname = DB_NAME, user = DB_USER, password = DB_PASSWORD, host = DB_HOST)
	cur = conn.cursor()
	cur.execute('SELECT * FROM rgb_values')
	values_list = cur.fetchall()
	cur.close()
	conn.close()
	return values_list

#Given an id, returns a list with a singular color and rgbvalues from the database
def get_values_list(id):
	conn = psycopg2.connect(dbname = DB_NAME, user = DB_USER, password = DB_PASSWORD, host = DB_HOST)
	cur = conn.cursor()
	cur.execute('SELECT * FROM colors WHERE id='+str(id))
	color_attributes = cur.fetchall()
	cur.execute('SELECT * FROM rgb_values WHERE id='+str(id))
	color_values = cur.fetchall()
	cur.close()
	conn.close()
	return color_attributes, color_values
		    
@app.route('/', methods = ['GET', 'POST'])
def test():
	if request.method == 'POST':
		create_unknown_color(request)
		
	colors_list = get_colors_list()
	values_list = get_rgbvalues_list()
	return render_template('/Colors/main.html', colors_list = colors_list, values_list = values_list)

@app.route('/new-color')
def newcolortest():
	return render_template('/Colors/Color-card/create.html')

@app.route('/submit', methods = ['GET', 'POST'])
def submit():
	if request.method == 'POST':
		create_color_and_push(request.form)
		
	colors_list = get_colors_list()
	values_list = get_rgbvalues_list()
	return render_template('/Colors/main.html', colors_list = colors_list, values_list = values_list)
	
@app.route('/edit/<id>', methods= ['GET','PUT'])
def edit(id):
	if (request.method == 'PUT')  or ((request.args.get('_method') != None) and (request.args['_method'] == 'PUT')):
		update_color(request.args, id)
		
	color_atributes, color_values = get_values_list(id)
	return render_template('/Colors/Color-card/edit.html', color_atributes = color_atributes, color_values = color_values)

@app.route('/delete/<id>', methods = ['GET', 'DELETE'])
def delete(id):
	if (request.method == 'DELETE')  or ((request.args.get('_method') != None) and (request.args['_method'] == 'DELETE')):
		color_delete = db.session.get(Color, id)
		rgbvalues_delete = db.session.get(RGBValues, id)
		db.session.delete(color_delete)
		db.session.delete(rgbvalues_delete)
		db.session.commit()
		
	colors_list = get_colors_list()
	values_list = get_rgbvalues_list()
	return render_template('/Colors/main.html', colors_list = colors_list, values_list = values_list)
	
