#      Slim version
FROM python:3.10-slim

# Copy everything we need into the image
COPY edabot edabot
COPY api api
COPY requirements.txt requirements.txt
COPY setup.py setup.py

# Install everything
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install .

RUN mkdir /static

CMD uvicorn api.fast:app --host 0.0.0.0 --port $PORT
