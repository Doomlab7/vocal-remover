doit link: 
  python ./downloader/main.py {{ link }}

sc file:
  python inference.py --input "{{ file }}"

  ffmpeg -i {{ file }}_Instruments.wav "{{ file }}_Instruments.mp3"

