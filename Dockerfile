FROM pytorch/pytorch


COPY requirements.txt /app/requirements.txt

RUN pip install  -r /app/requirements.txt 

RUN apt update -y && \
    # apt upgrade -qq -y && \
    apt install -y libsndfile1 libgl1 libglib2.0-0 libsm6 libxrender1 libxext6


COPY . /app

ENTRYPOINT ["streamlit", "run", "/app/app.py"]
