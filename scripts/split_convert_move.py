"Splits mp4s downloaded from youtube, converts og and split to mp3, and moves to folder to be uploaded later"
from pathlib import Path

from automations import InferenceRequest
from automations import convert_mp4
from automations import convert_wav
from automations import run_inference

if __name__ == "__main__":
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
