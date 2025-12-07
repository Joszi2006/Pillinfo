FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the model during build
RUN python -c "from gliner import GLiNER; import os; os.environ['TOKENIZERS_PARALLELISM']='false'; GLiNER.from_pretrained('anthonyyazdaniml/gliner-biomed-large-v1.0-medication-regimen-ner')"

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT