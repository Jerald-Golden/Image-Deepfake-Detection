from flask import Flask, render_template, request, session , jsonify
import logging
from PIL import Image
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
from flask_dance.contrib.google import make_google_blueprint, google
from dotenv import load_dotenv
import os
from flask_mail import Mail, Message
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
dotenv_path = os.path.join('credentials', '.env')
load_dotenv(dotenv_path)
app = Flask(__name__)
app.secret_key = "KjhLJF54f6ds234H"
uploads_dir = os.path.join('uploads')
os.makedirs(uploads_dir, exist_ok=True)
app.logger.disabled = True
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)
blueprint = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_to="model"
)
app.register_blueprint(blueprint, url_prefix="/login")
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = os.getenv("MAIL_PORT")
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
model_path = os.path.join('model', 'custom_model.h5')
loaded_model = load_model(model_path)
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array / 255.0
def predict_single_image(img_path, model):
    processed_image = preprocess_image(img_path)
    prediction = model.predict(processed_image)
    probability = prediction[0][0]
    predicted_class = "fake" if probability >= 0.5 else "real"
    return predicted_class, probability
@app.route('/')
def home():
    background_image = "/static/image1.jpg"
    return render_template('index.html', background_image=background_image)
@app.route('/login/google')
def login():
    background_image = "/static/image5.png"
    if not google.authorized:
        return render_template('login.html', background_image=background_image)
    resp = google.get("/oauth2/v2/userinfo")
    assert resp.ok, resp.text
    email = resp.json()["email"]
    session['Loggedin'] = True
    session['email'] = email
    return render_template('model.html', background_image=background_image)
@app.route('/contact.html')
def contact():
    background_image = "/static/image3.jpg"
    return render_template('contact.html', background_image=background_image)
@app.route('/about.html')
def about():
    background_image = "/static/image2.jpg"
    return render_template('about.html', background_image=background_image)
@app.route('/index.html')
def home1():
    background_image = "/static/image1.jpg"
    return render_template('index.html', background_image=background_image)
@app.route('/logout')
def home2():
    background_image = "/static/image1.jpg"
    return render_template('index.html', background_image=background_image)
@app.route("/getmail", methods=['POST'])
def send_mail():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    try:
        msg = Message('Response Mail', sender=os.getenv("MAIL_USERNAME"), recipients=[os.getenv("MAIL_RECIPIENT1")])
        msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        mail.send(msg)
        msg1 = Message('Response Mail', sender=os.getenv("MAIL_USERNAME"), recipients=[os.getenv("MAIL_RECIPIENT2")])
        msg1.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        mail.send(msg1)
        return jsonify({"message": "Mail sent successfully", "status": "success"})
    except Exception as e:
        return jsonify({"message": str(e), "status": "error"})
@app.route('/model.html', methods=['GET', 'POST'])
def model():
    background_image = "/static/image5.png"
    results = []
    if request.method == 'POST':
        for file in request.files.getlist('image_files[]'):
            try:
                file_path = os.path.join(uploads_dir, file.filename)
                file.save(file_path)
                predicted_class, probability = predict_single_image(file_path, loaded_model)
                if predicted_class == "real":
                    probability = 100 - probability
                if predicted_class == "fake":
                    probability = 100 * probability
                file_label = f"File: {file.filename}"
                result_label = f"Predicted Class: {predicted_class}\nProbability: {probability:.2f}%"
                results.append((file_label, result_label))
                os.remove(file_path)
            except Exception as e:
                print(f"Error saving file: {e}")
        return render_template('model.html', results=results, background_image=background_image)
    else:
        return render_template('model.html', background_image=background_image)
print("The Website:-"+"http://127.0.0.1:5000/")
if __name__ == "__main__":
    app.run(debug=True)