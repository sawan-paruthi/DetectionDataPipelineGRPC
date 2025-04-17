import os
import io
from flask import Flask, request, render_template, jsonify
from app import upload_image_to_grpc, send_log_entry_to_grpc  # Import the existing function
import json
import time
import ast

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
LOG_FILE = 'response_logs.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

log_entry = {}


def log_response_data(log_entry):    
    # Load existing logs if available
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []

    # Append new log entry
    logs.append(log_entry)

    # Write updated logs back to the file
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=4)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
async def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file part in the request"}), 400
    
    file = request.files['image']
    model_name = request.form['model']
    print(f"model name at clientside is {model_name}")

    if file.filename == '':

        return jsonify({"error": "No selected file"}), 400
    
    if file:
        # file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        # file.save(file_path)
        # ip_address = request.remote_addr
        # log_entry['ip_address'] = ip_address
        start_time = time.time()
        in_memory_file = io.BytesIO(file.read())

        # Use the video_file_generator directly from app.py grpc 
        response = await upload_image_to_grpc(in_memory_file, model_name)
        
        end_time = time.time()

        grpc_system_response_time = (end_time-start_time)*1000  # time in milli-seconds
        log_entry['grpc_system_response_time'] = grpc_system_response_time

        print("gRPC Response:", response)

        # Return the gRPC response
        return jsonify({
            "success": response.success,
            "message": response.message,
            "process_time": round(response.process_time,4),
            "grpc_response_time": round(grpc_system_response_time,4),
            "throughput": round(response.throughput,4),
            "power": round(response.power,4)
        })

    


@app.route('/log_round_trip_time', methods=['POST'])
async def log_round_trip_time():
    # round_trip_time = request.form.get('round_trip_time')
    if request:
        response = await send_log_entry_to_grpc(request)

        # log_response_data(log_entry)

        return jsonify({
            "message": response.message,  
            "success": response.success
        })
    else:
        return jsonify({"error": "Round-trip time not provided"}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)  