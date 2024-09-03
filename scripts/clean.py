from pathlib import Path

if __name__ == "__main__":
    # delete .mp4 and .wav in raw
    for file in Path("/app/downloads/raw").glob("*"):
        if file.suffix == ".mp4" or file.suffix == ".wav":
            file.unlink()
