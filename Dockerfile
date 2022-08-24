FROM python:3.10-alpine

RUN mkdir /src

COPY . /src

RUN cd /src && pip install .

WORKDIR /workdir

ENTRYPOINT [ "mvnb" ]
