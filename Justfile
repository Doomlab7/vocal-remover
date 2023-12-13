download-split-upload link: 
  echo "downloading yt video, converting, splitting, uploading"
  python ./download_yt_split_upload.py.py {{ link }}

split-convert-upload-clean:
  echo "converting for church, splitting, uploading"
  python ./scripts/split_convert_upload_instrumental_clean.py
