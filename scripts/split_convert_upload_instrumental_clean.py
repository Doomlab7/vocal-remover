"""Splits mp3s and just uploads the instrumentals to Olivet Bible Instrumentals

1. Download mp3 to split and put in downloads/just-split-convert/
2. `just split-convert-upload-clean`
"""
import os
from pathlib import Path

from automations import InferenceRequest
from automations import convert_wav
from automations import run_inference
from webdav3.client import Client

PASSWORD = os.environ.get("NC_PASSWORD")
TARGET = os.environ.get("NC_INSTRUMENTALS_ONLY_TARGET")
URL = os.environ.get("NC_URL")
USER = os.environ.get("NC_USER")

if __name__ == "__main__":
    for file in Path("/home/nic/third-party/vocal-remover/downloads/just-split-convert").glob("*.mp3"):
        inference_data = InferenceRequest(filename=str(file))
        data = InferenceRequest(filename=str(file.with_suffix('')))
        # run inference
        run_inference(inference_data)
    for file in Path("/home/nic/third-party/vocal-remover/downloads/just-split-convert").glob("*_Instruments.wav"):
        data = InferenceRequest(filename=str(file.with_suffix('')))
        # convert _instruments.wav to _instruments.mp3
        convert_wav(data)


    options = {
        "webdav_hostname": URL,
        "webdav_login": USER,
        "webdav_password": PASSWORD,
    }
    client = Client(options)
    client.verify = True
    # breakpoint()
    for file in Path("/home/nic/third-party/vocal-remover/downloads/just-split-convert/").glob("*_Instruments.mp3"):
        client.upload_file(remote_path=f"/{TARGET}/{file.name}", local_path=str(file))
        # unlink after upload
        file.unlink()
