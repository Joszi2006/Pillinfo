import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("ANTHROPIC_API_KEY")
NER_MODEL_NAME = os.getenv("NER_MODEL_NAME")
OCR_MODEL_NAME = os.getenv("OCR_MODEL_NAME")
FRONTEND_URL = os.getenv("FRONTEND_URL")
OPENFDA_BASE_URL = os.getenv("OPENFDA_BASE_URL")
OPENFDA_API_KEY = os.getenv("OPENFDA_API_KEY")  
OPENFDA_TIMEOUT = int(os.getenv("OPENFDA_TIMEOUT"))
RXNORM_BASE_URL = os.getenv("RXNORM_BASE_URL")
RXNORM_TIMEOUT = int(os.getenv("RXNORM_TIMEOUT"))
FRONTEND_URL = os.getenv("FRONTEND_URL")