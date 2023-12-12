doit link: 
  python ./downloader/main.py {{ link }}

sc file:
  python inference.py --input "{{ file }}"
  echo "deesn't work cause {{ file }} has extension in it!"
  ffmpeg -i {{ file }}_Instruments.wav "{{ file }}_Instruments.mp3"

