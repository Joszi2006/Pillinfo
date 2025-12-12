FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the GLiNER model
RUN python -c "from gliner import GLiNER; import os; os.environ['TOKENIZERS_PARALLELISM']='false'; GLiNER.from_pretrained('Ihor/gliner-biomed-small-v1.0')"

# Copy backend code
COPY backend/ .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT