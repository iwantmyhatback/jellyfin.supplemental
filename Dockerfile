FROM python:latest

ARG DIRNAME
ARG PYENV_LOCATION

COPY . $DIRNAME
WORKDIR $DIRNAME
EXPOSE 443
EXPOSE 80

ENV PATH="$PYENV_LOCATION/bin:$PATH"

RUN python3 -m venv $PYENV_LOCATION
RUN pip install -r requirements.txt
RUN chmod +x shell/main.sh