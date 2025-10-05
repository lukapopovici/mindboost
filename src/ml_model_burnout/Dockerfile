FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY predict_service.py ./

EXPOSE 8000

CMD ["flask", "--app", "predict_service", "run", "--host=0.0.0.0", "--port=8000"]
