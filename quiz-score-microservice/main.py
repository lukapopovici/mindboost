from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "mindboost")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "quiz_scores")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

app = Flask(__name__)

@app.route("/submit-score", methods=["POST"])
def submit_score():
    data = request.get_json(force=True)
    user = data.get("user")
    score = data.get("score")
    quiz_name = data.get("quiz_name")
    date = data.get("date", datetime.utcnow().isoformat())
    if not user or score is None or not quiz_name:
        return jsonify({"error": "Missing required fields"}), 400
    entry = {
        "user": user,
        "score": score,
        "quiz_name": quiz_name,
        "date": date
    }
    collection.insert_one(entry)
    return jsonify({"status": "success", "entry": entry})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010)
