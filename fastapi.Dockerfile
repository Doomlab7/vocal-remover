FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN python3 -m pip install uv

ENV VIRTUALENV=/app/.venv
RUN uv venv

RUN uv pip install -r requirements.app.txt -n

ENTRYPOINT [ "python", "app.py" ]


