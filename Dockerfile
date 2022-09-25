FROM python:3.10.5-alpine3.16

# Install alpine dependencies
RUN apk add --update curl
RUN apk add --update g++ zeromq-dev libffi-dev
RUN rm -rf /var/cache/apk/*

# Adds non privileged user
RUN addgroup --system user && \
    adduser --system user --ingroup user --shell /bin/sh
USER user

# Upgrades pip and installs poetry
ENV PATH="/home/user/.local/bin:$PATH"
RUN python -m pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /home/user/src/app

COPY pyproject.toml .
#RUN poetry config virtualenvs.create false  # Not working bc Permission issues (idk)
RUN poetry run python -m pip install --upgrade pip

COPY poetry.lock .
RUN poetry install

COPY . .

CMD ["poetry", "run", "python", "bot.py"]
