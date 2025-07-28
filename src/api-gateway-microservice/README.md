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

1. Clone the repository:
   ```
   git clone <repository-url>
   cd api-gateway-microservice
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the API Gateway microservice:
   ```
   python src/main.py
   ```

## Usage

- The API Gateway exposes endpoints that can be used to interact with the PDF parsing microservice and the Amazon Bedrock API.
- Refer to the `src/routes/gateway.py` file for the available routes and their usage.

## Notes

- Ensure that the PDF parsing microservice and the Amazon Bedrock API are accessible from the API Gateway.
- Modify the configuration as necessary to suit your environment.