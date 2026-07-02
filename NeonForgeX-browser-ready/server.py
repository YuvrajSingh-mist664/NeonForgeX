from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")
leaderboard = []


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/save_score", methods=["POST"])
def save_score():
    data = request.get_json(silent=True) or {}
    leaderboard.append(data)
    return jsonify({"status": "saved"})


@app.route("/leaderboard")
def get_scores():
    return jsonify(leaderboard)


if __name__ == "__main__":
    app.run(debug=True)
