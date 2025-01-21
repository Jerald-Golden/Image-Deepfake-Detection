from flask import Flask, render_template, request, send_from_directory
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
import os

app = Flask(__name__)
uploads_dir = os.path.join('uploads')
os.makedirs(uploads_dir, exist_ok=True)

# Load the model
model_path = os.path.join('model', 'custom_model.h5')
loaded_model = load_model(model_path)

# Preprocess image
def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array / 255.0

# Predict image class
def predict_single_image(img_path, model):
    processed_image = preprocess_image(img_path)
    prediction = model.predict(processed_image)
    probability = prediction[0][0]
    predicted_class = "fake" if probability >= 0.5 else "real"
    return predicted_class, probability

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(uploads_dir, filename)

@app.route('/', methods=['GET', 'POST'])
def model_page():
    results = []
    if request.method == 'POST':
        for file in os.listdir(uploads_dir):
            os.remove(os.path.join(uploads_dir, file))
        
        for file in request.files.getlist('image_files[]'):
            try:
                file_path = os.path.join(uploads_dir, file.filename)
                file.save(file_path)

                predicted_class, probability = predict_single_image(file_path, loaded_model)
                probability = 100 * probability if predicted_class == "fake" else 100 - (100 * probability)

                results.append({
                    "file_path":file_path,
                    "file_name": file.filename,
                    "predicted_class": predicted_class.capitalize(),
                    "probability": f"{probability:.2f}%"
                })
            except Exception as e:
                print(f"Error processing file: {e}")
    
    return render_template('index.html', results=results)

if __name__ == "__main__":
    print("The Website: http://127.0.0.1:5000/")
    app.run(debug=True)
