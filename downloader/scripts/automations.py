import re
import subprocess

from fastapi import HTTPException
from pydantic import BaseModel


class DownloadRequest(BaseModel):
    link: str

class InferenceRequest(BaseModel):
    filename: str

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
        # Run pytube command to get video information
        result = subprocess.run(f"pipx run pytube {data.link} --list", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Access the stdout and stderr
        stdout_result = result.stdout.decode('utf-8')
        stderr_result = result.stderr.decode('utf-8')

        # TODO: parse the output and find the highest quality audio itag
        itag = get_itag(stdout_result)

        # Run pytube command to download the video with the selected itag
        result_download = subprocess.run(f"pipx run pytube {data.link} --itag {itag} --target /home/nic/third-party/vocal-remover/downloads/raw", shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Access the stdout and stderr of the download command
        stdout_download = result_download.stdout.decode('utf-8')
        stderr_download = result_download.stderr.decode('utf-8')

        return {"message": "File downloaded", "stdout": stdout_result + '\n' + stdout_download, "stderr": stderr_result + '\n' + stderr_download}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error running pytube command: {e}")


def run_inference(data: InferenceRequest):
    filename = data.filename
    inference_script = "/home/nic/third-party/vocal-remover/.venv/vocal-remover/bin/python /home/nic/third-party/vocal-remover/inference.py --output_dir /home/nic/third-party/vocal-remover/downloads/raw/"

    # Run the inference script
    try:
        subprocess.run(f"{inference_script} --input '{filename}'", shell=True, check=True)
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
