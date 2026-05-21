FROM python:3.13-slim
LABEL maintainer="IcePack"
ENV PYTHONUNBUFFERED=1 

COPY ./requirements.txt /tmp/requirements.txt
COPY . /Judicial

WORKDIR /Judicial
EXPOSE 6000

ARG PIP_INDEX_URL=https://pypi.org/simple
RUN python -m venv /ViPy && \
    /ViPy/bin/pip install -i https://mirror-pypi.runflare.com/simple --upgrade pip && \
    /ViPy/bin/pip install -i https://mirror-pypi.runflare.com/simple -r /tmp/requirements.txt && \
    rm -rf /tmp && \
    # /ViPy/bin/pip install --upgrade pip && \
    # /ViPy/bin/pip install -i ${PIP_INDEX_URL} -r /tmp/requirements.txt && \
    # rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user
      
ENV PATH="/ViPy/bin:$PATH"

USER django-user
