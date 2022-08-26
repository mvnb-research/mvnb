# Builder
FROM python:3.10-alpine as builder

RUN apk add yarn && pip install pdm

COPY . /src

RUN cd /src && pdm build -v

# Main
FROM python:3.10-alpine

COPY --from=builder /src/dist/ /dist

RUN pip install --no-cache /dist/*.whl && \
    find / -type f -name '*.py[co]' -delete && \
    find / -type d -name __pycache__ -delete && \
    rm -rf /dist

WORKDIR /workdir

ENTRYPOINT [ "mvnb" ]
