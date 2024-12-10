download-split-upload link: 
  echo "downloading yt video, converting, splitting, uploading"
  python ./download_yt_split_upload.py {{ link }}

split-convert-upload-clean:
  echo "converting for church, splitting, uploading"
  /var/home/nic/projects/personal/vocal-remover/.venv/bin/python ./scripts/split_convert_upload_instrumental_clean.py

docker:
  docker pull pypeaday/vocal-remover-app
  docker run -p 8001:8001 --name vocal-remover --rm pypeaday/vocal-remover-app
