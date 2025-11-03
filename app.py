import requests
from flask import Flask, request, render_template, send_file
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

API_URL = "https://ocr.asprise.com/api/v1/receipt"
API_KEY = "TEST"

def clear_uploaded_files():
    # Remove all files in the upload directory
    for fname in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, fname)
        if os.path.isfile(path):
            os.remove(path)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Always clear previous data on GET (page reload)
    if request.method == 'GET':
        clear_uploaded_files()
        return render_template('index.html', extracted_json=None, download_url=None)
    # POST: handle invoice upload and extraction
    if request.method == 'POST':
        clear_uploaded_files()
        file = request.files['invoice']
        save_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(save_path)

        # API call
        with open(save_path, "rb") as f:
            response = requests.post(
                API_URL,
                data={'api_key': API_KEY, 'recognizer': 'auto'},
                files={'file': f}
            )
        invoice_json = response.text

        # Save output
        output_json_path = os.path.join(UPLOAD_FOLDER, "invoice_output.json")
        with open(output_json_path, "w") as fout:
            fout.write(invoice_json)

        return render_template(
            'index.html',
            extracted_json=invoice_json,
            download_url='/download'
        )

@app.route('/download')
def download_json():
    output_json_path = os.path.join(UPLOAD_FOLDER, "invoice_output.json")
    if os.path.exists(output_json_path):
        return send_file(output_json_path, as_attachment=True)
    else:
        # If download attempted without extraction, show homepage as fresh
        return render_template('index.html', extracted_json=None, download_url=None)

if __name__ == "__main__":
    app.run(debug=True)
