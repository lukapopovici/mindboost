
# MindBoost
MindBoost AI: An Intelligent Study Companion

## Microservices Architecture

This project is organized as a set of independent microservices:

- **backend**: API Gateway microservice (routes requests to other services)
- **pdf-parser-microservice**: Parses PDF files and extracts text
- **bedrock-client-microservice**: Handles communication with Amazon Bedrock
- **frontend**: React app for the user interface

Each microservice is self-contained and can be run independently. See each service's README for details.

### Running the Microservices

1. **Backend (API Gateway)**
   - Directory: `src/backend`
   - Run: `uvicorn src.main:app --reload`

2. **PDF Parser**
   - Directory: `src/pdf-parser-microservice`
   - Run: `uvicorn src.main:app --reload`

3. **Bedrock Client**
   - Directory: `src/bedrock-client-microservice`
   - Run: `uvicorn src.main:app --reload`

4. **Frontend**
   - Directory: `src/frontend`
   - Run: `npm start`

---

See each microservice's README for API endpoints and further setup instructions.

