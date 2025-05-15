import os
from flask import Flask, render_template, request, redirect, url_for
import pytesseract
from PIL import Image
import re
from datetime import datetime
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Image Processing Functions
def preprocess_image(image_path):
    """Enhance image for better OCR"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def extract_chart_data(image_path):
    """Extract DOB and planetary positions"""
    processed_img = preprocess_image(image_path)
    text = pytesseract.image_to_string(processed_img)
    
    # Extract data (customize these patterns)
    dob = re.search(r'DOB[: ]+(\d{2}/\d{2}/\d{4})', text).group(1)
    planets = {
        'sun': {'degree': 25.5, 'sign': 'leo'},
        'moon': {'degree': 12.3, 'sign': 'cancer'}
        # Add more planets...
    }
    return dob, planets

# Routes
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST' and 'chart_image' in request.files:
        file = request.files['chart_image']
        if file and file.filename.split('.')[-1].lower() in app.config['ALLOWED_EXTENSIONS']:
            filename = f"user_upload_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            dob, planets = extract_chart_data(filepath)
            return render_template('results.html', 
                                birth_date=dob,
                                planetary_data=planets)
    
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
