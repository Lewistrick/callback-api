FROM python:3.11

RUN mkdir /app
WORKDIR /app

COPY README.md .
COPY pyproject.toml .

RUN python -m venv .venv
RUN . /app/.venv/bin/activate && \
    python -m pip install --upgrade pip && \
    python -m pip install poetry && \
    poetry install --without dev,test

COPY localhost.* .
COPY run_app.sh .
COPY main.py .


CMD ["sh", "run_app.sh"]