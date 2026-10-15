from flask import Flask, request, jsonify
import datetime

app = Flask(__name__)

FILE_LOG = "esp32_data_log.txt"

@app.route("/energy", methods=['POST'])

def energy_handler():
    # Get data from HTTP POST
    raw_data = request.get_data(as_text=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Print data to console
    print(f"[{timestamp}] Data arrived: {raw_data}")

    # Write ti file log
    with open(FILE_LOG, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {raw_data}\n")

    # HTTP return
    return jsonify({"status": "success", "message": "Data Arrive"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=45000, debug=True)