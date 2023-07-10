FROM python:3.12.0a5-alpine3.17
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install beautifulsoup4
COPY . /
ENTRYPOINT ["python3", "loudy.py"]
CMD ["--config", "config.json"]
