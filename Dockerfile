FROM python:3.8
ENV PYTHONUNBUFFERED 1
RUN mkdir /server

RUN ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone
RUN apt-get update
RUN apt-get install vim -y
RUN /usr/local/bin/python -m pip install --upgrade pip
COPY ./config/apiserver_gcp.json /server/config/apiserver_gcp.json
COPY ./py-requirements /py-requirements
RUN pip install -r /py-requirements/prod.txt
COPY . /server/

RUN rm /server/.env
RUN cp /server/.env.prod /server/.env
RUN export GOOGLE_CLOUD_PROJECT="apiserver"
WORKDIR /server/src
EXPOSE 8080 8000

CMD exec gunicorn apiserver.wsgi:application -b :$PORT --workers=1 --threads 4 --reload --env ENV="prod" --preload