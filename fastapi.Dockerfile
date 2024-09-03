# FROM python:3.10-slim
FROM pytorch/pytorch

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN python3 -m pip install uv

ENV PATH=/app/.venv/bin:$PATH
ENV VIRTUAL_ENVIRONMENT=/app/.venv
RUN uv venv

RUN uv pip install -r requirements.app.txt -r requirements.txt -n

ENTRYPOINT [ "python", "app.py" ]


