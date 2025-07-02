FROM python:3.13-slim

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV

WORKDIR /api-flask

COPY ./backend/ backend/
COPY ../../parsing/ parsing/

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 5011

CMD ["python", "backend/Server.py"]

