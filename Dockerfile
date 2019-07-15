from python:3.7

copy . /app

RUN apt-get update --fix-missing
RUN apt-get install --fix-missing
RUN apt-get -y install build-essential




run make clean -C /app/fahes_service && make -C /app/fahes_service
run pip install -r /app/requirements.txt
workdir /app
entrypoint ["python", "app.py"]
