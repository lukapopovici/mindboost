# API Gateway Microservice

This project implements an API Gateway microservice that connects to a separate microservice responsible for parsing PDF files and making requests to the Amazon Bedrock API to return questions.

## Project Structure

```
api-gateway-microservice
├── src
│   ├── main.py               # Entry point of the API Gateway microservice
│   ├── routes
│   │   └── gateway.py        # Defines routes for the API Gateway
│   ├── services
│   │   ├── pdf_parser_client.py  # Client for interacting with the PDF parsing microservice
│   │   └── bedrock_client.py      # Client for communicating with the Amazon Bedrock API
│   └── utils
│       └── __init__.py       # Initialization file for the utils package
├── requirements.txt           # Lists project dependencies
└── README.md                  # Documentation for the project
```


## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <repository-url>
   cd api-gateway-microservice
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Create a `.env` file:**
   - Copy the provided `.env.example` or create a new `.env` file in this directory.
   - Add your Amazon Bedrock API key and any other secrets:
     ```env
     AWS_BEARER_TOKEN_BEDROCK=your-bedrock-api-key
     BEDROCK_REGION=us-east-1
     BEDROCK_MODEL_ID=anthropic.claude-v2
     ```

4. **Set up AWS credentials:**
   - Make sure your AWS credentials (with Bedrock access) are available, e.g. via `~/.aws/credentials`, environment variables, or IAM role.

5. **Run the API Gateway microservice:**
   ```sh
   python src/main.py
   ```

6. **Test the endpoints:**
   - Use a tool like Postman or `curl` to POST to `/api/parse-pdf` (with a PDF file) or `/api/ask-bedrock` (with a JSON body containing a `question`).

## Usage

- The API Gateway exposes endpoints that can be used to interact with the PDF parsing microservice and the Amazon Bedrock API.
- Refer to the `src/routes/gateway.py` file for the available routes and their usage.

## Notes

- Ensure that the PDF parsing microservice and the Amazon Bedrock API are accessible from the API Gateway.
- Modify the configuration as necessary to suit your environment.