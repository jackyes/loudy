FROM python:3
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /
ENTRYPOINT ["python3", "noisy.py"]
CMD ["--config", "config.json"]
