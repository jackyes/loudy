FROM python:3.13.0b3-alpine3.20
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install beautifulsoup4
COPY . /
ENTRYPOINT ["python3", "loudy.py"]
CMD ["--config", "config.json"]
