FROM python:3.10.5-alpine3.16

RUN apk add --update curl
RUN apk add --update g++ zeromq-dev libffi-dev
RUN rm -rf /var/cache/apk/*

RUN python -m pip install --upgrade pip
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

ENV PATH /root/.poetry/bin:$PATH

USER user
WORKDIR /usr/src/app

COPY pyproject.toml .
RUN poetry run python -m pip install --upgrade pip

COPY poetry.lock .
RUN poetry install

COPY . .

CMD ["poetry", "run", "python", "bot.py"]
