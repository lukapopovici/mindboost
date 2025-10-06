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

Send a POST request to `/predict` with the above input format to receive a burnout probability and feature introspection.

# MindBoost
MindBoost AI: An Intelligent Study Companion

## Microservices Architecture



This project is organized as a set of independent microservices:

- **backend**: API Gateway microservice (routes requests to other services)
- **pdf-parser-microservice**: Parses PDF files and extracts text
- **bedrock-client-microservice**: Handles communication with Amazon Bedrock
- **knowledge-graph-microservice**: Accepts a PDF and returns a knowledge graph (nodes/links) for visualization in the frontend (e.g., with Recharts)
- **ml-model-burnout**: Machine learning microservice for predicting burnout risk from time series data (Flask-based, uses a trained ML model)
- **frontend**: React app for the user interface

Each microservice is self-contained and can be run independently. See each service's README for details.

All services can also be run together using Docker Compose:

```sh
docker-compose up --build
```

This will start all microservices, including the ML model for burnout prediction, and expose their respective ports.



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

6. **Frontend**
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

