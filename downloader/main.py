import logging
import os
from argparse import ArgumentParser
from pathlib import Path

from scripts.automations import DownloadRequest
from scripts.automations import InferenceRequest
from scripts.automations import convert_mp4
from scripts.automations import convert_wav
from scripts.automations import run_inference
from scripts.automations import youget
from webdav3.client import Client

PASSWORD = os.environ.get("NC_PASSWORD")
TARGET = os.environ.get("NC_TARGET")
URL = os.environ.get("NC_URL")
USER = os.environ.get("NC_USER")

# Configure logging to both console and a file
logging.basicConfig(filename='app.log', level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Reused paths
downloads_path = Path("/home/nic/third-party/vocal-remover/downloads")
raw_path = downloads_path / "raw"
mp3s_path = downloads_path / "mp3s"
to_upload_path = mp3s_path / "to-upload"
uploaded_path = mp3s_path / "uploaded"

if __name__ == "__main__":

    raise SystemExit(1)
    logger = logging.getLogger(__name__)

    parser = ArgumentParser()
    parser.add_argument("link")
    args = parser.parse_args()
    link = DownloadRequest(link=args.link)

    # Download
    youget(link)
    logger.info("Download complete")

    # Process downloaded files
    for file in raw_path.glob("*.mp4"):
        inference_data = InferenceRequest(filename=str(file))
        data = InferenceRequest(filename=str(file.with_suffix('')))

        # Run inference
        run_inference(inference_data)

        # Convert mp4 to mp3
        convert_mp4(data)

    for file in raw_path.glob("*_Instruments.wav"):
        data = InferenceRequest(filename=str(file.with_suffix('')))
        # Convert _instruments.wav to _instruments.mp3
        convert_wav(data)

    # Move .mp3s to to_upload
    for move_these in raw_path.glob("*.mp3"):
        move_these.rename(to_upload_path / move_these.name)

    # Upload to Nextcloud
    options = {
        "webdav_hostname": URL,
        "webdav_login": USER,
        "webdav_password": PASSWORD,
    }
    client = Client(options)
    client.verify = True
    for file in to_upload_path.glob("*.mp3"):
        client.upload_file(remote_path=f"/{TARGET}/{file.name}", local_path=str(file))
        logger.info(f"Uploaded: {file.name}")
        # Move file from to-upload to uploaded
        file.rename(uploaded_path / file.name)

    # Delete .mp4 and .wav in raw
    for file in raw_path.glob("*"):
        if file.suffix == ".mp4" or file.suffix == ".wav":
            file.unlink()
            logger.info(f"Deleted: {file.name}")
