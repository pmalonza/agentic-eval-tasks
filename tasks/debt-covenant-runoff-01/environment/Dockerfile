# Agent runtime image. This task only needs to read CSV/text files and
# write JSON + Markdown, so a minimal Python image is sufficient -- no
# heavier scientific stack is required.
FROM python:3.11-slim

RUN pip install --no-cache-dir pandas==2.2.* numpy==1.26.*

# Harbor does not mount task files into the container: data reaches the
# agent only through what's baked into the image.
COPY data/ /home/agent/data/

WORKDIR /home/agent
RUN mkdir -p /home/agent/results
