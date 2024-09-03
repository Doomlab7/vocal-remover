import logging
import os
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

from webdav3.client import Client

from inference import main as inference_main
from scripts.automations import DownloadRequest
from scripts.automations import InferenceRequest
from scripts.automations import convert_mp4
from scripts.automations import convert_wav
from scripts.automations import youget

PASSWORD = os.environ.get("NC_PASSWORD")
TARGET = os.environ.get("NC_TARGET")
URL = os.environ.get("NC_URL")
USER = os.environ.get("NC_USER")

# Configure logging to both console and a file
logging.basicConfig(
    filename="downloader.main.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

# Reused paths
downloads_path = Path("/app/downloads")
raw_path = downloads_path / "raw"
mp3s_path = downloads_path / "mp3s"
to_upload_path = mp3s_path / "to-upload"
uploaded_path = mp3s_path / "uploaded"


@dataclass
class Args:
    gpu = -1
    pretrained_model = "models/baseline.pth"
    input: str = None
    sr: int = 44100
    n_fft: int = 2048
    hop_length: int = 1024
    batchsize: int = 4
    cropsize: int = 256
    output_image: bool = False
    postprocess: bool = False
    tta: bool = False
    output_dir: str = ""


def main(args):
    link = DownloadRequest(link=args.link)

    logging.info(f"Downloading: {link}")

    # import time
    # time.sleep(5)
    #
    # raise SystemExit(1)
    #
    # Download
    youget(link)
    logging.info("Download complete")
    print("Download complete")

    # Process downloaded files
    for file in raw_path.glob("*.mp4"):
        inference_data = InferenceRequest(filename=str(file))
        data = InferenceRequest(filename=str(file.with_suffix("")))

        # Run inference
        # run_inference(inference_data)
        args = Args(
            input=inference_data.filename,
            output_dir="/app/downloads/raw/",
        )
        inference_main(args)

        # Convert mp4 to mp3
        convert_mp4(data)

    for file in raw_path.glob("*_Instruments.wav"):
        data = InferenceRequest(filename=str(file.with_suffix("")))
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
        logging.info(f"Uploaded: {file.name}")
        # Move file from to-upload to uploaded
        file.rename(uploaded_path / file.name)

    # Delete .mp4 and .wav in raw
    for file in raw_path.glob("*"):
        if file.suffix == ".mp4" or file.suffix == ".wav":
            file.unlink()
            logging.info(f"Deleted: {file.name}")


if __name__ == "__main__":
    logging = logging.getlogging(__name__)

    parser = ArgumentParser()
    parser.add_argument("link")
    args = parser.parse_args()
    main(args)
