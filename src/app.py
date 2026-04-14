from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Bienvenue sur mon API", "status": "ok"})

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/hello/<name>")
def hello(name):
    return jsonify({"message": f"Bonjour {name} !"})

if __name__ == "__main__":
    app.run(debug=True)