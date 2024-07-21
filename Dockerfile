FROM ubuntu:latest

RUN apt update && apt upgrade -y && apt install python3 -y && apt install python3-pip -y && apt install git -y && apt install python3.12-venv -y && apt autoremove -y

RUN git clone https://github.com/DavidLSB/Colors-web.git

WORKDIR /Colors-web

RUN python3 -m venv venv

RUN . venv/bin/activate 

RUN venv/bin/pip install -r requirements.txt

