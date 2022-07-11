# Vocal Remover App

This is my [streamlit]() app based on [tsurumeso's vocal-remover project](https://github.com/tsurumeso/vocal-remover)

My app doesn't do anything with the vocal tracks - if anyone is using this and wants it let me know and I'll add it.

## Getting started

1. `git clone https://github.com/nicpayne713/vocal-remover-app.git`
2. `docker-compose build`
3. `docker-compose up`
4. Go to [http://localhost:8501](http://localhost:8501)

## Traefik

I put this behind my reverse proxy - those labels are in the docker-compose file, you can edit for your own use case or delete them

## TODOs

[] - python venv in docker
[] - mp4 example in readme
[] - deploy on heroku or something as example?
[] - tweet tweet

# Original READ

# vocal-remover

[![Release](https://img.shields.io/github/release/tsurumeso/vocal-remover.svg)](https://github.com/tsurumeso/vocal-remover/releases/latest)
[![Release](https://img.shields.io/github/downloads/tsurumeso/vocal-remover/total.svg)](https://github.com/tsurumeso/vocal-remover/releases)

This is a deep-learning-based tool to extract instrumental track from your songs.

## Installation

### Getting vocal-remover
Download the latest version from [here](https://github.com/tsurumeso/vocal-remover/releases).

### Install PyTorch
**See**: [GET STARTED](https://pytorch.org/get-started/locally/)

### Install the other packages
```
cd vocal-remover
pip install -r requirements.txt
```

## Usage
The following command separates the input into instrumental and vocal tracks. They are saved as `*_Instruments.wav` and `*_Vocals.wav`.

### Run on CPU
```
python inference.py --input path/to/an/audio/file
```

### Run on GPU
```
python inference.py --input path/to/an/audio/file --gpu 0
```

### Advanced options
`--tta` option performs Test-Time-Augmentation to improve the separation quality.
```
python inference.py --input path/to/an/audio/file --tta --gpu 0
```

`--postprocess` option masks instrumental part based on the vocals volume to improve the separation quality.  
**Experimental Warning**: If you get any problems with this option, please disable it.
```
python inference.py --input path/to/an/audio/file --postprocess --gpu 0
```

## Train your own model

### Place your dataset
```
path/to/dataset/
  +- instruments/
  |    +- 01_foo_inst.wav
  |    +- 02_bar_inst.mp3
  |    +- ...
  +- mixtures/
       +- 01_foo_mix.wav
       +- 02_bar_mix.mp3
       +- ...
```

### Train a model
```
python train.py --dataset path/to/dataset --reduction_rate 0.5 --mixup_rate 0.5 --gpu 0
```

## References
- [1] Jansson et al., "Singing Voice Separation with Deep U-Net Convolutional Networks", https://ismir2017.smcnus.org/wp-content/uploads/2017/10/171_Paper.pdf
- [2] Takahashi et al., "Multi-scale Multi-band DenseNets for Audio Source Separation", https://arxiv.org/pdf/1706.09588.pdf
- [3] Takahashi et al., "MMDENSELSTM: AN EFFICIENT COMBINATION OF CONVOLUTIONAL AND RECURRENT NEURAL NETWORKS FOR AUDIO SOURCE SEPARATION", https://arxiv.org/pdf/1805.02410.pdf
- [4] Liutkus et al., "The 2016 Signal Separation Evaluation Campaign", Latent Variable Analysis and Signal Separation - 12th International Conference
