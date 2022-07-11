import os
import sys
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from threading import current_thread

import librosa
import numpy as np
import pydub
import soundfile as sf
import streamlit as st
import torch
from streamlit.scriptrunner.script_run_context import SCRIPT_RUN_CONTEXT_ATTR_NAME

from inference import Separator
from lib import nets, spec_utils

MODEL_PATH = "/app/models/baseline.pth"


def inference_main(
    input,
    sample_rate: int = 44100,
    n_fft: int = 2048,
    hop_length: int = 1024,
    batchsize: int = 4,
    cropsize: int = 256,
    postprocess: bool = False,
    tta: bool = False,
):
    pretrained_model = MODEL_PATH
    print("loading model...", end=" ")
    device = torch.device("cpu")
    model = nets.CascadedNet(n_fft, 32, 128)
    model.load_state_dict(torch.load(pretrained_model, map_location=device))
    # if torch.cuda.is_available() and args.gpu >= 0:
    #     device = torch.device("cuda:{}".format(args.gpu))
    #     model.to(device)
    print("done")

    print("loading wave source...", end=" ")
    X, sr = librosa.load(
        input, sample_rate, False, dtype=np.float32, res_type="kaiser_fast"
    )
    basename = os.path.splitext(os.path.basename(input))[0]
    print("done")

    if X.ndim == 1:
        # mono to stereo
        X = np.asarray([X, X])

    print("stft of wave source...", end=" ")
    X_spec = spec_utils.wave_to_spectrogram(X, hop_length, n_fft)

    print("done")

    sp = Separator(model, device, batchsize, cropsize, postprocess)

    if tta:
        y_spec, v_spec = sp.separate_tta(X_spec)
    else:
        y_spec, v_spec = sp.separate(X_spec)

    print("validating output directories...", end=" ")
    os.makedirs("/app-data/instrumentals/", exist_ok=True)
    os.makedirs("/app-data/vocals/", exist_ok=True)
    print("done")

    print("inverse stft of instruments...", end=" ")
    wave = spec_utils.spectrogram_to_wave(y_spec, hop_length=hop_length)

    print("done")
    sf.write("{}{}.wav".format("/app-data/instrumentals/", basename), wave.T, sr)

    # eventually use diretories instead of mutating song names - should make a database easier
    # mp3 conversion
    instrumental_output_file = f"/app-data/instrumentals/{basename}.wav"
    instrumental_output_mp3 = f"/app-data/instrumentals/{basename}.mp3"

    print("converting to mp3...", end=" ")
    sound = pydub.AudioSegment.from_wav(instrumental_output_file)
    sound.export(instrumental_output_mp3, format="mp3")
    print("done")

    print("inverse stft of vocals...", end=" ")
    wave = spec_utils.spectrogram_to_wave(v_spec, hop_length=hop_length)
    print("done")
    sf.write("{}{}.wav".format("/app-data/vocals/", basename), wave.T, sr)

    # eventually use diretories instead of mutating song names - should make a database easier
    # mp3 conversion
    vocal_output_file = f"/app-data/vocals/{basename}.wav"
    vocal_output_mp3 = f"/app-data/vocals/{basename}.mp3"

    print("converting to mp3...", end=" ")
    sound = pydub.AudioSegment.from_wav(vocal_output_file)
    sound.export(vocal_output_mp3, format="mp3")
    print("done")

    return instrumental_output_mp3, vocal_output_mp3


@contextmanager
def st_redirect(src, dst):
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)

    with StringIO() as buffer:
        old_write = src.write

        def new_write(b):
            if getattr(current_thread(), SCRIPT_RUN_CONTEXT_ATTR_NAME, None):
                buffer.write(b)
                output_func(buffer.getvalue())
            else:
                old_write(b)

        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write


@contextmanager
def st_stdout(dst):
    with st_redirect(sys.stdout, dst):
        yield


@contextmanager
def st_stderr(dst):
    with st_redirect(sys.stderr, dst):
        yield


def main():
    instrumental_output_mp3 = ""
    vocal_output_mp3 = ""

    with st.form("song_form"):
        data = st.file_uploader("Upload mp3 to split instrumentals from", type=["mp3"])
        use_tta = st.checkbox(
            "TTA - option performs Test-Time-Augmentation to improve the separation quality."
        )
        use_postprocess = st.checkbox(
            "Use Postprocessing option masks instrumental part based on the vocals volume to improve the separation quality. **EXPERIMENTAL ACCORDING TO MAINTAINER OF VOAL-REMOVER REPO** "
        )

        submitted = st.form_submit_button("Punch it Chewy!")
        if submitted:
            with st_stdout("success"):
                print("Reading Data\n")
                audio_bytes = data.read()

                # write out to file until I figure out how to just pass audio_bytes to the inference script
                print("Saving to staging file")
                with open(f"/app-data/{data.name}", "wb") as outfile:
                    outfile.write(audio_bytes)
                # allow listening to song through app as sanity check
                # st.audio(audio_bytes, format="audio/mp3")
            with st_stdout("code"):
                instrumental_output_mp3, vocal_output_mp3 = inference_main(
                    f"/app-data/{data.name}"
                )

            with open(instrumental_output_mp3, "rb") as f:
                instrumental_output_bytes = f.read()
            # allow listening to song through app as sanity check
            st.write("Have a listen to the instrumental!")
            st.audio(instrumental_output_bytes, format="audio/mp3")

            with open(vocal_output_mp3, "rb") as f:
                vocal_output_bytes = f.read()
            # allow listening to song through app as sanity check
            st.write("Have a listen to the vocals!")
            st.audio(vocal_output_bytes, format="audio/mp3")

    # TODO: download it...
    st.markdown("### Once the song is split you will be able to download below")
    try:
        suffix = "-Instrumental"
        if use_tta:
            suffix += ".tta"
        if use_postprocess:
            suffix += ".postprocess"
        with open(instrumental_output_mp3, "rb") as f:
            st.download_button(
                "Download Instrumentals",
                f,
                file_name=Path(instrumental_output_mp3).stem + f"{suffix}.mp3",
            )
        with open(vocal_output_mp3, "rb") as f:
            st.download_button(
                "Download Vocals",
                f,
                file_name=Path(vocal_output_mp3).stem + f"{suffix}.mp3",
            )
    except FileNotFoundError:
        with st_stdout("error"):
            print("Still waiting...")


if __name__ == "__main__":
    st.markdown("# Audacity who??")
    st.markdown(
        "**Upload one mp3 at a time and the vocal-remover app will strip the instrumentals from the vocals. There are 2 options to play with and you can listen to the instrumental/vocal tracks separately from here before downloading**"
    )
    main()
