FROM python:latest

ENV DIRNAME="jellyfin-supplemental"
COPY . $DIRNAME
WORKDIR $DIRNAME
EXPOSE 443
EXPOSE 80

ENV VIRTUAL_ENV="./pythonEnvironment"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m venv $VIRTUAL_ENV
RUN pip install -r requirements.txt
RUN chmod +x main.sh