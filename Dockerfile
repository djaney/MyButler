FROM python:3
ADD requirements.txt /
RUN apt-get update
RUN apt-get install sphinxbase-utils python3-dev alsa-base alsa-utils libasound-dev portaudio19-dev libportaudio2 libpulse-dev libportaudiocpp0 libav-tools swig espeak -y
RUN apt-get install libttspico0 libttspico-utils libttspico-data

RUN pip3 install -r requirements.txt
CMD ["app/main.py"]
