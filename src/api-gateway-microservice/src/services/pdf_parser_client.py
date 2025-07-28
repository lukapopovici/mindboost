from flask import requests

class PDFParserClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def parse_pdf(self, pdf_file):
        with open(pdf_file, 'rb') as file:
            response = requests.post(f"{self.base_url}/parse", files={'file': file})
            response.raise_for_status()
            return response.json()