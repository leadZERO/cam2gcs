FROM alpine:3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk add --no-cache ffmpeg python3-dev py3-pip gcc musl-dev libffi-dev
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip3 --no-cache install -r requirements.txt
COPY ./cam2gcs.py .

ENV GOOGLE_APPLICATION_CREDENTIALS=/etc/.gcskeys.json

CMD ["python3", "cam2gcs.py"]
