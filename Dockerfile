from python:3.7

copy . /app

RUN apt-get update --fix-missing
RUN apt-get install --fix-missing
RUN apt-get -y install ubuntu-make


workdir /app/fahes_srvice
run make
run pip install -r /app/requirements.txt
workdir /app
entrypoint ["python", "app.py"]
