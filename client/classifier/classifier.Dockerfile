FROM python:3.13-slim

ENV VIRTUAL_ENV=/opt/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV

WORKDIR /api-flask/client/classifier/

COPY parsing/ /api-flask/parsing/
COPY dataset/ /api-flask/dataset/
COPY client/classifier/ .

# <Magic trick> to always get a `.env` file (take `.env.example`).
RUN if [ ! -e .env ]; then cp .env.example .env; fi
# </Magic trick>

# <Initialize the labelled dataset>
RUN cd ../../dataset/ && python ready_to_classify.py && cd - && \
    mv ../../dataset/ready_to_classify/data_depth_3.json data/data_depth_3.json
# </Initialize the labelled dataset>

RUN pip install --upgrade pip

# <Flask + gevent + socketio>
RUN pip install --no-cache-dir -r requirements/flask_requirements.txt
# </Flask + gevent + socketio>

# <LLM Labellizer>
RUN variable=$(cat .env | grep "CLASSIFIER_CATEGORIZER_USE" | cut -d '=' -f2);\
    if [ "$variable" = "TRUE" ]; then\
        pip install --no-cache-dir\
            -r requirements/categorizer_requirements.txt; fi
# </LLM Labellizer>

# <Tokenizer + Embeddings>
RUN variable=$(cat .env | grep "CLASSIFIER_MISCELLANEOUS_USE" | cut -d'=' -f2);\
    if [ "$variable" = "TRUE" ]; then\
        pip install --no-cache-dir\
            -r requirements/miscellenaous_requirements.txt; fi
# </Tokenizer + Embeddings>

# <Model TFIDF>
RUN variable=$(cat .env | grep "CLASSIFIER_TFIDF_USE" | cut -d '=' -f2);\
    if [ "$variable" = "TRUE" ]; then\
        pip install --no-cache-dir\
            -r requirements/tfidf_requirements.txt;\
        pip install --no-cache-dir\
            -r requirements/miscellenaous_requirements.txt; fi
# </Model TFIDF>

EXPOSE 5011

CMD gunicorn 'app:app' \
    --worker-class gevent \
    --workers 1 \
    --bind 0.0.0.0:5011 \
    --reload \
    --access-logfile - \
    --error-logfile -

