from flask import 
Flask,render_template,request,redirect,url_for,send_file,session,jsonify
import mysql.connector
from fuzzywuzzy import fuzz
from PIL import Image
import io
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = '12345678' 
db_connection = mysql.connector.connect(
 host="localhost",
 user="root",
 password="root",
 database="medicine"
)
@app.route('/')
def home():
 return render_template('search1.html')
@app.route('/results')
def results():
 user_input = request.args.get('user_input')
 image_url = url_for('display_image', medicine_name=user_input)
 current_use = request.args.get('current_use')
 product_info = request.args.getlist('product_info')
 medicine_result=request.args.get('user_input')
 prices= request.args.getlist('prices')
 similarity_threshold = 80
 similar_medicines_data=find_similar_medicines(similarity_threshold, 
current_use)
similar_medicines = [(med['med_name'], med['med_price']) for med in 
similar_medicines_data]
 med_price=request.args.getlist('med_price')
 med_name=request.args.getlist('similar_medicines.med_nareturn 
 render_template('result.html',user_input=user_input,image_url=image_url,current_
use=current_use,product_info=product_info,med_name=med_name,similar_medic
ines=similar_medicines,prices=prices,med_price=med_price,medicine_result=med
icine_result,)
@app.route('/search', methods=['POST','GET'])
def search():
 user_input = request.form.get('search-bar')
 image_url = url_for('display_image', medicine_name=user_input)
 similarity_thresholds=40
 search_result= search_medicine(user_input)
 search_resul= search_medicine_by_uses(user_input,similarity_thresholds)
 product_r=search_product_info(user_input)
 prices=price(user_input)
 if search_result[0]: # Check if search_result is not None
 image_url=image_url
 current_use = search_result
 product_info = product_r
 medicine_result=search_result
 return 
redirect(url_for('results',user_input=user_input,image_url=image_url,current_use=
current_use,product_info=product_info,prices=prices,search_result=search_result,
medicine_result=medicine_result))
 elif search_medicine_by_uses(user_input,similarity_thresholds):
 search_resul=search_resul
 return render_template('results.html',search_resul=search_resul)
 else:
 return render_template('Nomedicinefound.html',user_input= user_input) 
@app.route('/login', methods=['GET', 'POST'])
def login():

 if request.method == 'POST':
 username = request.form['username']
 password = request.form['password']
 # Check if the provided username and password are correct (implement your 
own logic here)
 if username == 'admin' and password == 'password':
 session['logged_in'] = True
 return render_template('adds.html')
 else:
 return 'Login failed. Please try again.'
 return render_template('login.html')
#To display image by taking medicine name as input 
@app.route('/display_image/<medicine_name>')
def display_image(medicine_name):
 cursor = db_connection.cursor(dictionary=True)
 cursor.execute("SELECT * FROM medicine.tablets WHERE medicine_name 
LIKE %s", (medicine_name+'%',))
 medicine_result = cursor.fetchone()
 if medicine_result:
 med_image = medicine_result['medicine_name']
 cursor.execute("SELECT * FROM medicine.tphotos WHERE 
medicine_name LIKE %s", (med_image+'%',))
 image_data = cursor.fetchone()
 if image_data:
 # Convert binary data to an image
 image = Image.open(io.BytesIO(image_data.get('photos',b'')))
 # Save the image to a temporary file
 temp_image_path = 'temp_image.png'
 image.save(temp_image_path, 'PNG')
 # Send the image file to the browser
 return send_file(temp_image_path, mimetype='image/png')
 # If no image is found, return a placeholder or an error image
 return send_file('error_image.png', mimetype='image/png')
#to search tablet by tablet name 
@app.route('/search_medicine')
def search_medicine(medicine_name):
 cursor = db_connection.cursor(dictionary=True)
 # Search for medicine by partial name
 cursor.execute("SELECT * FROM medicine.tablets WHERE medicine_name 
LIKE %s", (medicine_name+'%',))
 medicine_results = cursor.fetchall()
 current_use = []
 if medicine_results:
 for medicine_result in medicine_results:
 print(" ")
 print(f"Medicine: {medicine_result['medicine_name']}")
 print(f"Uses: {medicine_result['current_use']}")
 medicine_name=medicine_name
 current_use.append(medicine_result['current_use'])
 else:
 print("No medicine found")
 return None, None
 cursor.close()
 return current_use
def search_product_info(medicine_name):
 cursor = db_connection.cursor(dictionary=True)
 #search for product informations
 cursor.execute("SELECT * FROM medicine.tablets WHERE medicine_name 
LIKE %s", (medicine_name+'%',))
 medicine_result = cursor.fetchone()
 product_info=[]
 if medicine_result:
 cursor.execute("SELECT * FROM medicine.tableinfo WHERE med_id 
= %s", (medicine_result['med_id'],))
 product_results = cursor.fetchall()
 if product_results:
 print("\nProduct information:")
 for product_result in product_results:

 product_info.append(product_result['product_info'])
 else:
 print("No related products found.")
 else:
 print("No medicine found.")
 cursor.close()
 return product_info
# Function to retrieve medicines with similar uses
@app.route('/find_similar_medicines')
def find_similar_medicines(similarity_threshold, current_use):
 cursor = db_connection.cursor(dictionary=True)
 #cursor.execute("SELECT medicine_name,current_use FROM 
medicine.tablets")
 #cursor.execute("SELECT t.medicine_name,t.current_use FROM 
medicine.tablets t JOIN medicine.tableinfo p ON t.medicine_name = 
p.medicine_name")
 cursor.execute("SELECT t.medicine_name, t.current_use, ti.product_info, 
ti.price FROM medicine.tablets t INNER JOIN medicine.tableinfo ti ON 
t.medicine_name = ti.medicine_name")
 results = cursor.fetchall()
 cursor.close()
 similar_medicines_data = []
 for medicine_result in results:
 similarity_score = 
fuzz.token_set_ratio(current_use,medicine_result['current_use'])
 if similarity_score >= similarity_threshold: 
similar_medicines_data.append({'med_name':medicine_result['medicine_name'],'
med_price':medicine_result['price']})
 else:
 print("No medicines with similar uses found.")
 return similar_medicines_data
