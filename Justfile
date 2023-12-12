download-split-upload link: 
  echo "downloading yt video, converting, splitting, uploading"
  python ./downloader/main.py {{ link }}

split-convert-upload-clean:
  echo "converting for church, splitting, uploading"
  python ./downloader/scripts/split_convert_upload_instrumental_clean.py
