import streamlit as st
import pymongo
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("DB_NAME", "mindboost")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "interests")

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

st.set_page_config(page_title="Interest Monitor", layout="wide")
st.title("Interest Monitor - Relevant Topics")

entries = list(collection.find().sort("date", -1))

if entries:
	st.write(f"Total interests logged: {len(entries)}")
	for entry in entries:
		st.markdown(f"### {entry.get('paper_title', 'Unknown Paper')}")
		st.write(f"**User:** {entry.get('user', 'N/A')}")
		st.write(f"**Date:** {entry.get('date', 'N/A')}")
		st.write(f"**Relevant Topics:**")
		st.code(entry.get('interest', ''), language='text')
else:
	st.info("No interests logged yet.")