import re
import subprocess
from typing import List
from typing import Optional

import pytube
from fastapi import HTTPException
from pydantic import BaseModel


class DownloadRequest(BaseModel):
    link: str

class InferenceRequest(BaseModel):
    filename: str

class StreamInfo(BaseModel):
    itag: str
    mime_type: str
    res: Optional[str]
    fps: Optional[str]
    vcodec: Optional[str]
    acodec: Optional[str]
    progressive: bool
    type: str
    abr: Optional[str]

class YouTubeStreamsInfo(BaseModel):
    streams: List[StreamInfo]

def convert_mp4(data: InferenceRequest):
    filename = data.filename
    mp4 = f"'{filename}.mp4'"
    mp3 = f"'{filename}.mp3'"

    # Run ffmpeg command to convert mp4 to mp3
    try:
        subprocess.run(f"ffmpeg -i {mp4} {mp3}", shell=True, check=True)
        return {"message": f"FFmpeg conversion completed for {filename}"}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error running ffmpeg command")

def convert_wav(data: InferenceRequest):
    filename = data.filename
    instruments_wav = f"'{filename}.wav'"
    instruments_mp3 = f"'{filename}.mp3'"

    # Run ffmpeg command to convert wav to mp3
    try:
        subprocess.run(f"ffmpeg -i {instruments_wav} {instruments_mp3}", shell=True, check=True)
        return {"message": f"FFmpeg conversion completed for {filename}"}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error running ffmpeg command")

def youget(data: DownloadRequest):
    try:
        streams = pytube.YouTube(data.link).streams
        itag = get_itag(streams)
        filepath = pytube.YouTube(data.link).streams.get_by_itag(itag).download('/home/nic/personal/vocal-remover/downloads/raw')

        return {"message": f"File downloaded: {filepath}"}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error running pytube command: {e}")


def run_inference(data: InferenceRequest):
    # replace this with just imoprting the inference.main function - nesting in scripts/ made the import here basically impossible
    filename = data.filename
    inference_script = "/home/nic/personal/vocal-remover/.venv/vocal-remover/bin/python /home/nic/personal/vocal-remover/inference.py --output_dir /home/nic/personal/vocal-remover/downloads/raw/"

    # Run the inference script
    try:
        subprocess.run(f"{inference_script} --input '{filename}'", shell=True, check=True)
        return {"message": f"Inference completed for {filename}"}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Error running inference script")

def get_itag(streams: YouTubeStreamsInfo):
    # Filter audio streams with mime_type "audio/mp4"
    audio_streams = [stream for stream in streams if stream.type == "audio" and stream.mime_type == "audio/mp4"]

    if not audio_streams:
        return None  # No matching audio streams found

    # Find the stream with the highest abr value
    highest_abr_stream = max(audio_streams, key=lambda stream: int(stream.abr.replace("kbps", "") or 0), default=None)

    return highest_abr_stream.itag

def get_itag_from_stdout(output: str):
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
