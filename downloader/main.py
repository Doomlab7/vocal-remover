import os
from argparse import ArgumentParser
from pathlib import Path

from automations import DownloadRequest
from automations import InferenceRequest
from automations import convert_mp4
from automations import convert_wav
from automations import run_inference
from automations import youget
from webdav3.client import Client

PASSWORD = os.environ.get("NC_PASSWORD")
TARGET = os.environ.get("NC_TARGET")
URL = os.environ.get("NC_URL")
USER = os.environ.get("NC_USER")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("link")
    args = parser.parse_args()
    link = DownloadRequest(link=args.link)
    # download
    youget(link)

    # run inference and convert each downloaded file (it's only one, doing it this way so I don't have to know the filename apriori)
    for file in Path("/home/nic/third-party/vocal-remover/downloads/raw").glob("*.mp4"):
        inference_data = InferenceRequest(filename=str(file))
        data = InferenceRequest(filename=str(file.with_suffix('')))
        # run inference
        run_inference(inference_data)
        # convert og mp4 to mp3
        convert_mp4(data)

    for file in Path("/home/nic/third-party/vocal-remover/downloads/raw").glob("*_Instruments.wav"):
        data = InferenceRequest(filename=str(file.with_suffix('')))
        # convert _instruments.wav to _instruments.mp3
        convert_wav(data)

    # move .mp3s to to_upload
    for move_these in Path("/home/nic/third-party/vocal-remover/downloads/raw").glob("*.mp3"):
        move_these.rename(Path("/home/nic/third-party/vocal-remover/downloads/mp3s/to-upload") / move_these.name)

    # upload to nextcloud
    options = {
        "webdav_hostname": URL,
        "webdav_login": USER,
        "webdav_password": PASSWORD,
    }
    client = Client(options)
    client.verify = True
    for file in Path("/home/nic/third-party/vocal-remover/downloads/mp3s/to-upload/").glob("*.mp3"):
        client.upload_file(remote_path=f"/{TARGET}/{file.name}", local_path=str(file))
        # move file from to-upload to uploaded
        file.rename(Path("/home/nic/third-party/vocal-remover/downloads/mp3s/uploaded") / file.name)

    # delete .mp4 and .wav in raw
    for file in Path("/home/nic/third-party/vocal-remover/downloads/raw").glob("*"):
        if file.suffix == ".mp4" or file.suffix == ".wav":
            file.unlink()
