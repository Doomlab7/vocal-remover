import re
import subprocess

from fastapi import HTTPException
from pydantic import BaseModel


class DownloadRequest(BaseModel):
    link: str

class InferenceRequest(BaseModel):
    filename: str

def run_ffmpeg(data: InferenceRequest):
    filename = data.filename
    instruments_wav = f"{filename}_instruments.wav"
    instruments_mp3 = f"{filename}_instruments.mp3"

    # Run ffmpeg command to convert wav to mp3
    try:
        subprocess.run(f"ffmpeg -i {instruments_wav} {instruments_mp3}", shell=True, check=True)
        return {"message": f"FFmpeg conversion completed for {filename}"}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error running ffmpeg command")
def youget(data: DownloadRequest):
    # Run ffmpeg command to convert wav to mp3
    try:
        r = subprocess.run(f"pipx run pytube {data.link} --list", shell=True, check=True)
        # TODO: parse the output and find the highest quality audio itag
        itag = get_itag(r)
        subprocess.run(f"pipx run pytube {data.link} --itag {itag}", shell=True, check=True)
        return {"message": "File downloaded"}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error running ffmpeg command")


def run_inference(data: InferenceRequest):
    filename = data.filename
    inference_script = "python inference.py"

    # Run the inference script
    try:
        subprocess.run(f"{inference_script} --input {filename}", shell=True, check=True)
        return {"message": f"Inference completed for {filename}"}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error running inference script")

def get_itag(output: str):
# Split the output into lines
    lines = output.split("\n")

# Initialize variables to store the maximum abr and corresponding itag
    max_abr = 0
    max_abr_itag = None

# Iterate through the lines
    for line in lines:
        if "mime_type=\"audio/mp4\"" in line:
            # Extract abr value using regular expression
            abr_match = re.search(r'abr="(\d+)kbps"', line)
            if abr_match:
                current_abr = int(abr_match.group(1))
                # Update max_abr and max_abr_itag if current_abr is greater
                if current_abr > max_abr:
                    max_abr = current_abr
                    max_abr_itag_match = re.search(r'itag="(\d+)"', line)
                    if max_abr_itag_match:
                        max_abr_itag = max_abr_itag_match.group(1)

# Print the result
    print(f"Max abr: {max_abr}")
    print(f"Corresponding itag: {max_abr_itag}")
    return max_abr_itag
