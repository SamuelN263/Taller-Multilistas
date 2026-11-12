from flask import Flask, jsonify, render_template
from multilista import load_divipola

app = Flask(__name__)
MULTILISTA = load_divipola("data/DIVIPOLA.csv")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/multilista")
def api_multilista():
    return jsonify(MULTILISTA.to_dict())


if __name__ == "__main__":
    app.run(debug=True, port=5002)
