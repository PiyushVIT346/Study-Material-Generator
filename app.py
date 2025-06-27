from flask import Flask, render_template, request, redirect, url_for
from backend import StudyMaterialGenerator  # Replace with your actual filename
import os
import json
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

generator = StudyMaterialGenerator()

# In-memory store for simplicity (consider Redis or DB for production)
temp_storage = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/get-started')
def get_started():
    return render_template('topic_input.html')

@app.route('/generate', methods=['POST'])
def generate():
    topic = request.form.get('topic', '').strip()
    if not topic:
        return redirect(url_for('get_started'))

    try:
        study_material = generator.generate_study_material(topic)

        # Generate unique ID to store data
        material_id = str(uuid.uuid4())
        temp_storage[material_id] = study_material

        return redirect(url_for('result', material_id=material_id))
    except Exception as e:
        return f"❌ Error generating study material: {str(e)}"

@app.route('/result/<material_id>')
def result(material_id):
    study_material = temp_storage.get(material_id)
    if not study_material:
        return redirect(url_for('get_started'))

    return render_template('result.html', study_material=study_material)

if __name__ == '__main__':
    app.run(debug=True)
