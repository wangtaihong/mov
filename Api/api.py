# coding=utf-8
from flask import Flask, jsonify, request
from app import put_work, content, categories

app = Flask(__name__)
app.debug = True

@app.route("/api/")
def hello():
    return "Hello World!"

@app.route('/api/put_task', methods=['POST'])
def put_task():
    # im = request.files['im'].stream.read()
    # r = predict_captcha(im)
    r = put_work.put(request.get_json())
    return jsonify(r)

@app.route('/api/content/<_id>')
def get_content(_id):
    print(_id)
    r = content.get(_id)
    return jsonify(r)

@app.route('/api/categories',methods=['GET'])
def get_categories():
    r = categories.get()
    return jsonify(r)

if __name__ == "__main__":
    app.run(host='0.0.0.0')