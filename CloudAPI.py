from flask import Flask, request, jsonify
from cloudCache import cache

app = Flask(__name__)


@app.route("/recognize", methods=["POST"])
def hello_world():
    fileImg = request.files['media']
    return jsonify({'ts': cache.request(fileImg)}), 200
