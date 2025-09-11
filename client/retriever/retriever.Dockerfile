FROM python:3.13-slim

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /api-flask

RUN python -m venv $VIRTUAL_ENV

COPY client/retriever .

# <Magic trick> to always get a `.env` file (take `.env.example`).
RUN if [ ! -e .env ]; then cp .env.example .env; fi
# </Magic trick>

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

EXPOSE 5001

CMD gunicorn 'app:app' \
    --worker-class gevent \
    --workers 4 \
    --bind 0.0.0.0:5001 \
    --reload \
    --access-logfile - \
    --error-logfile -

