import os
import schedule
import subprocess
import tempfile
import time

from datetime import datetime
from google.cloud import storage


def get_env_config():
  return {
    'camera': {
      'username': os.environ['CAMERA_USERNAME'],
      'password': os.environ['CAMERA_PASSWORD'],
      'hostpath': os.environ['CAMERA_HOSTPATH'],
      'name': os.environ['CAMERA_NAME'],
    },
    'gcs_bucket': {
      'name': os.environ['GCS_BUCKET_NAME'],
      'path': os.environ['GCS_BUCKET_PATH']
    },
    'refresh': os.environ['REFRESH'] #seconds
  }


def make_camera_url(hostpath, user='', pwd=''):
    s = 'rtsp://'
    if user != '':
        s += user

        if pwd != '':
            s += f':{pwd}'

    if s != 'rtsp://':
        return f'{s}@{hostpath}'
    return hostpath


def get_and_write_camera_frame(camera_url, fname):
    cmd = f'ffmpeg -loglevel error -rtsp_transport tcp -y -i "{camera_url}" -vframes 1 {fname}'
    subprocess.call(cmd, shell=True)


def get_temp_filename():
    _, fn = tempfile.mkstemp('.jpg')
    return fn


def get_current_datetimestr():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def job():
  conf = get_env_config()

  camera_url = make_camera_url(
    conf['camera']['hostpath'],
    conf['camera']['username'],
    conf['camera']['password']
  )

  fn = get_temp_filename()

  get_and_write_camera_frame(camera_url, fn)
  gcs = storage.Client()
  bucket = gcs.bucket(conf['gcs_bucket']['name'])
  blob_name = f"{conf['gcs_bucket']['path'].strip('/')}/{conf['camera']['name']}_{get_current_datetimestr()}.jpg"
  blob = bucket.blob(blob_name)
  blob.upload_from_filename(fn)
  blob.content_type = 'image/jpeg'
  blob.patch()
  os.remove(fn)


if __name__ == '__main__':
  job()
  schedule.every(int(get_env_config()['refresh'])).seconds.do(job)
  print(schedule.jobs)

  while True:
    schedule.run_pending()
    time.sleep(1)
