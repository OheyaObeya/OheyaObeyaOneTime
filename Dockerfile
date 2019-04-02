FROM jjanzic/docker-python3-opencv:opencv-3.4.1 
LABEL maintainer="komo_fr"

ARG project_dir=/OheyaObeya/

ADD OheyaObeyaOneTime $project_dir
WORKDIR /OheyaObeya/

RUN git clone https://github.com/OheyaObeya/OheyaObeyaOneTime.git

WORKDIR /OheyaObeya/OheyaObeyaOneTime

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
