FROM python:3.13-slim

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV

WORKDIR /api-flask/client/classifier/

COPY parsing/ /api-flask/parsing/
COPY client/classifier/ .

# <Magic trick> to always get a `.env` file (take `.env.example`).
RUN if [ ! -e .env ]; then cp .env.example .env; fi
# </Magic trick>

RUN pip install --upgrade pip \
&& pip install --no-cache-dir -r requirements.txt

EXPOSE 5011

CMD ["python", "app.py"]

