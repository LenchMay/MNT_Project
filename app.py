from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/contacts')
def contacts():
    cnt = '1. Elena<br>' \
    '2. Nikolay'
    return cnt

if __name__ == '__main__':
    app.run(debug=True, port=8088)