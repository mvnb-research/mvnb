# Builder
FROM python:3.11-alpine as builder

RUN apk add make npm

COPY . /src

RUN cd /src && make build

# Main
FROM python:3.11-alpine

COPY --from=builder /src/dist/ /dist

RUN pip install --no-cache /dist/*.whl && \
    find / -type f -name '*.py[co]' -delete && \
    find / -type d -name __pycache__ -delete && \
    rm -rf /dist

WORKDIR /workdir

ENTRYPOINT [ "mvnb" ]
