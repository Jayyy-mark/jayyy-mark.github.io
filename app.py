from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
  return "Hello from server"

app.run(debug=False, host="0.0.0.0")
