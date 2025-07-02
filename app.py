from flask import Flask, render_template, request, redirect, url_for
from backend import StudyMaterialGenerator
import os
import json
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

generator = StudyMaterialGenerator()
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
        material_id = str(uuid.uuid4())
        temp_storage[material_id] = study_material

        return redirect(url_for('result', material_id=material_id))
    except Exception as e:
        return f" Error generating study material: {str(e)}"

@app.route('/result/<material_id>')
def result(material_id):
    study_material = temp_storage.get(material_id)
    if not study_material:
        return redirect(url_for('get_started'))

    return render_template('result.html', study_material=study_material)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
