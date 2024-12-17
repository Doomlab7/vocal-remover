# FROM python:3.10-slim
FROM pytorch/pytorch

RUN apt-get update && apt-get install git ffmpeg libsm6 libxext6  -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PATH=/app/.venv/bin:$PATH
RUN uv venv

ENV VIRTUAL_ENVIRONMENT=/app/.venv
# don't need the app ones, but I don't want to refactor everything right now
RUN uv pip install -r requirements.watcher-app.txt -r requirements.txt -r requirements.app.txt -n

ENTRYPOINT [ "python", "watcher-app.py" ]


