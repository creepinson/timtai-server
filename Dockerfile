FROM python:latest

RUN apt update -y
RUN apt install -y libavcodec-dev libavformat-dev libswscale-dev libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev libjpeg-dev libpng-dev libwebp-dev libgtk-3-dev libgtkglext1 libgtkglext1-dev

WORKDIR /app
COPY . ./
RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD python3 -m timtai.main

