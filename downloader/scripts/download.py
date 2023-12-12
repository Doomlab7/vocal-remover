from argparse import ArgumentParser

from automations import DownloadRequest
from automations import youget

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("link")
    args = parser.parse_args()
    link = DownloadRequest(link=args.link)
    youget(link)
