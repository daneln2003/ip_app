from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    ip = requests.get("https://api.ipify.org").text
    return f"My public IP is: {ip}"

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
