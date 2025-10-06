
# MindBoost

MindBoost is an intelligent academic companion platform built as a set of microservices. It helps students and educators analyze study materials, generate knowledge graphs, create quizzes, track learning progress, and monitor academic well-being. The system integrates AI-powered document parsing, knowledge extraction, quiz generation, burnout prediction, and interest tracking, all accessible via a modern React frontend and orchestrated with Docker Compose.

## Burnout Predictor ML Model

The `ml-model-burnout` microservice uses a trained machine learning model to predict the probability that a user is close to burnout, based on a time series of scores (e.g., stress, wellbeing, or other relevant metrics).

**Model Details:**
- The model is loaded from a pickle file (`model.pkl`).
- It expects a set of features extracted from the user's score history.
- The prediction is a probability value between 0 and 1.

**Input Format (JSON):**
```
{
   "user_id": "u1",                   // optional; used in response
   "series": [
      {"date": "2025-01-05", "score": 82},
      {"date": "2025-01-12", "score": 78},
      {"date": "2025-01-20", "score": 74}
   ]
}
```

**Output Format (JSON):**
```
{
   "user_id": "u1",
   "prob_close_to_burnout": 0.78,
   "features": { ... } // extracted features used for prediction
}
```

- **backend**: API Gateway microservice (routes requests to other services)
- **pdf-parser-microservice**: Parses PDF files and extracts text
- **quiz-burnout-gateway**: Fetches user quiz data from MongoDB and feeds it to the burnout predictor, returning the result
- **mongodb**: NoSQL database for storing quiz scores and user data
9. **Interest Monitor Microservice**
   - Directory: `interest-monitor-microservice`
   - Run: `streamlit run app.py` (Frontend)
   - Purpose: Receives and displays relevant topics (interests) for papers, stores them in MongoDB, and shows them in a Streamlit dashboard
- **frontend**: React app for the user interface
This will start all microservices, including the ML model for burnout prediction, quiz scoring, burnout gateway, MongoDB, and monitoring, and expose their respective ports. You can interact with all features from the frontend at [http://localhost:3000](http://localhost:3000).


### Running the Microservices Individually

1. **Backend (API Gateway)**
   - Directory: `src/backend`
   - Run: `uvicorn src.main:app --reload`

2. **PDF Parser**
   - Directory: `src/pdf-parser-microservice`
   - Run: `uvicorn src.main:app --reload`

3. **Bedrock Client**
   - Directory: `src/bedrock-client-microservice`
   - Run: `uvicorn src.main:app --reload`

4. **Knowledge Graph**
   - Directory: `src/knowledge-graph-microservice`
   - Run: `uvicorn src.main:app --reload`


5. **ML Model Burnout Predictor**
   - Directory: `src/ml_model_burnout`
   - Run: `flask --app predict_service run --host=0.0.0.0 --port=8004`

6. **Quiz Score Microservice**
   - Directory: `quiz-score-microservice`
   - Run: `flask --app main run --host=0.0.0.0 --port=8010`

7. **Quiz Burnout Gateway**
   - Directory: `quiz-burnout-gateway`
   - Run: `flask --app main run --host=0.0.0.0 --port=8011`

8. **MongoDB**
   - Service: `mongodb` (NoSQL database)
   - Port: `27017`

9. **Bedrock Monitor**
   - Directory: `bedrock-monitor`
   - Run: `streamlit run app.py`
   - Port: `8501`

10. **Frontend**
    - Directory: `src/frontend`
    - Run: `npm start`


---

### Test Users for Development

These users are automatically added to the database for testing and login:

| Email               | Password      |
|---------------------|--------------|
| test1@example.com   | password123  |
| test2@example.com   | letmein456   |
| test3@example.com   | qwerty789    |

Use these credentials to log in during development and testing.

## Important!

When first setting it up and running the services, before trying to log in run the script in the src/misc folder after installing the dependecies in order to populate the database

```
pip install -r misc/requirements.txt

```
---

See each microservice's README for API endpoints and further setup instructions.

