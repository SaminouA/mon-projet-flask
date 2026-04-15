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


@app.route("/add/<a>/<b>")
def add(a, b):
    return jsonify({"result": int(a) + int(b)})


@app.route("/about")
def about():
    return jsonify({"app": "Mon projet Flask", "version": "1.0"})


# @app.route("/eval")
# def eval_route():
#     from flask import request
#     expr = request.args.get("expr", "1+1")
#     result = eval(expr)  # DANGEREUX !
#     return jsonify({"result": str(result)})


if __name__ == "__main__":
    app.run()
