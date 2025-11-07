from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return 'Quick start app: Hello World!'

@app.route('/test')
def test():
    return jsonify({'status': 'ok', 'message': 'Quick start server is running'})

if __name__ == '__main__':
    print('Starting quick start Flask app on 127.0.0.1:5000')
    app.run(host='127.0.0.1', port=5000, debug=True)
