# upload to nextcloud

import os
from pathlib import Path

from webdav3.client import Client

PASSWORD = os.environ.get("NC_PASSWORD")
TARGET = os.environ.get("NC_TARGET")
URL = os.environ.get("NC_URL")
USER = os.environ.get("NC_USER")

if __name__ == "__main__":
    options = {
        "webdav_hostname": URL,
        "webdav_login": USER,
        "webdav_password": PASSWORD,
    }
    client = Client(options)
    client.verify = True
    # breakpoint()
    for file in Path("/app/downloads/mp3s/to-upload/").glob("*.mp3"):
        client.upload_file(remote_path=f"/{TARGET}/{file.name}", local_path=str(file))
        # move file from to-upload to uploaded
        file.rename(Path("/app/downloads/mp3s/uploaded") / file.name)
