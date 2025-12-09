FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- RUN COMMAND WITH QUANTIZATION ---
RUN python -c " \
    from gliner import GLiNER; \
    from transformers import BitsAndBytesConfig; \
    import torch; \
    import os; \
    os.environ['TOKENIZERS_PARALLELISM']='false'; \
    quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float32); \
    GLiNER.from_pretrained('anthonyyazdaniml/gliner-biomed-large-v1.0-medication-regimen-ner', quantization_config=quant_config) \
"
# ---------------------------------------------

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
EXPOSE $PORT