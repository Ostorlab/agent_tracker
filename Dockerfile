FROM python:3.8-alpine as base
FROM base as builder
RUN apk add build-base
RUN apk update
RUN mkdir /install
WORKDIR /install
COPY requirement.txt /requirement.txt
RUN pip install --prefix=/install -r /requirement.txt
FROM base
COPY --from=builder /install /usr/local
RUN mkdir -p /app/agent
COPY agent /app/agent
COPY ostorlab.yaml /app/agent/ostorlab.yaml
WORKDIR /app
ENV PYTHONPATH=/app
CMD ["python3", "/app/agent/tracker_agent.py"]
