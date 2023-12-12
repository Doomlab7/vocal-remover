dlyt link:
  python ./downloader/download.py {{ link }}

sc:
  python /home/nic/personal/olivet-davinci-resolve-automation/downloader/split_and_convert.py

clean:
  python /home/nic/personal/olivet-davinci-resolve-automation/downloader/clean.py

upload:
  python /home/nic/personal/olivet-davinci-resolve-automation/downloader/upload.py

doit link: dlyt link sc clean upload
