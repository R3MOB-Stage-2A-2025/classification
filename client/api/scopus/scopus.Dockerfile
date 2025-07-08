FROM python:3.13-slim

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /api-flask

RUN python -m venv $VIRTUAL_ENV

COPY backend/requirements.txt .
COPY backend/.env .
COPY backend/Server.py .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 5004

CMD ["python", "Server.py"]

