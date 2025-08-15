from flask import Flask

app = Flask(_name_)

@app.route('/')
def home():
  return "Hello from server"

app.run(debug=False, host="0.0.0.0")
