FROM python:3.6

WORKDIR /

COPY requirements.txt /

RUN pip3 install -r requirements.txt

COPY k8s-job-cleaner.py /

CMD ["/k8s-job-cleaner.py"]
