from flask import Flask, request, jsonify

app = Flask(__name__)

leaderboard = []

@app.route("/save_score", methods=["POST"])
def save_score():
    data = request.json
    leaderboard.append(data)
    return jsonify({"status": "saved"})

@app.route("/leaderboard")
def get_scores():
    return jsonify(leaderboard)

app.run(debug=True)