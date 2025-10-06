from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from datetime import datetime

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "mindboost")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "interests")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

app = Flask(__name__)

@app.route("/submit-interest", methods=["POST"])
def submit_interest():
    data = request.get_json(force=True)
    user = data.get("user")
    interest = data.get("interest")
    paper_title = data.get("paper_title")
    date = data.get("date", datetime.utcnow().isoformat())
    if not user or not interest or not paper_title:
        return jsonify({"error": "Missing required fields"}), 400
    entry = {
        "user": user,
        "interest": interest,
        "paper_title": paper_title,
        "date": date
    }
    collection.insert_one(entry)
    return jsonify({"status": "success", "entry": entry})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8020)
