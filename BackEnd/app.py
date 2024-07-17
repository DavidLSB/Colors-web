from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
import psycopg2


MAX_CHARACTERS_STRING = 40
RELATED_COLORS_MAX_AMOUNT = 5
DB_HOST = "localhost"
DB_NAME = "colorsdb"
DB_USER = "postgres"
DB_PASSWORD = "password"

app = Flask(__name__, template_folder = '../FrontEnd')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://'+DB_USER+':'+DB_PASSWORD+'@'+DB_HOST+'/'+DB_NAME
app.app_context().push()
db = SQLAlchemy(app)
conn = psycopg2.connect(dbname = DB_NAME, user = DB_USER, password = DB_PASSWORD, host = DB_HOST)
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
		self.recipee_colores = recipee_colors

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

@app.route('/')
def home():
	return render_template('hub.html')
    
@app.route('/test')
def test():
	cur = conn.cursor()
	cur.execute('SELECT * FROM colors')
	colors_list = cur.fetchall()
	cur.execute('SELECT * FROM rgb_values')
	values_list = cur.fetchall()
	cur.close()
	return render_template('/Colors/main.html', colors_list = colors_list, values_list = values_list)

@app.route('/new-color')
def newcolortest():
	return render_template('/Colors/Color-card/create.html')

@app.route('/submit', methods = ['GET', 'POST'])
def submit():
	
	if request.method == 'POST':
		name = request.form['name']
		color_temperature = request.form['color_temperature']
		complementary_colors = request.form['complementary_colors']
		analogous_colors = request.form['analogous_colors']
		recipee_colors = request.form['recipee_colors']
		red = request.form['red']
		green = request.form['green']
		blue = request.form['blue']
		
		color = Color(name, color_temperature, complementary_colors, analogous_colors, recipee_colors)
		db.session.add(color)
		rgbvalues = RGBValues(red, green, blue)
		db.session.add(rgbvalues)
		db.session.commit()
		
	#if request.method == 'GET':
		cur = conn.cursor()
		cur.execute('SELECT * FROM colors')
		colors_list = cur.fetchall()
		cur.execute('SELECT * FROM rgb_values')
		values_list = cur.fetchall()
		cur.close()
	return render_template('/Colors/main.html', colors_list = colors_list, values_list = values_list) #render_template('success.html', data = name)
	
@app.route('/edit/<id>', methods= ['GET','POST'])
def edit(id):
	if request.method == 'POST':
		name = request.form['name']
		color_temperature = request.form['color_temperature']
		complementary_colors = request.form['complementary_colors']
		analogous_colors = request.form['analogous_colors']
		recipee_colors = request.form['recipee_colors']
		red = request.form['red']
		green = request.form['green']
		blue = request.form['blue']
		
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
		
	cur = conn.cursor()
	cur.execute('SELECT * FROM colors WHERE id='+str(id))
	color_atributes = cur.fetchall()
	cur.execute('SELECT * FROM rgb_values WHERE id='+str(id))
	color_values = cur.fetchall()
	cur.close()
	return render_template('/Colors/Color-card/edit.html', color_atributes = color_atributes, color_values = color_values)

@app.route('/delete/<id>', methods = ['GET', 'POST'])
def delete(id):
	if request.method == 'POST':
		cur = conn.cursor()
		cur.execute('DELETE FROM colors WHERE id = %s', id)
		conn.commit()
		cur.execute('DELETE FROM rgb_values WHERE id = %s', id)
		conn.commit()
		cur.close
	cur = conn.cursor()
	cur.execute('SELECT * FROM colors')
	colors_list = cur.fetchall()
	cur.execute('SELECT * FROM rgb_values')
	values_list = cur.fetchall()
	cur.close()
	return render_template('/Colors/main.html', colors_list = colors_list, values_list = values_list)
	
