FROM registry.access.redhat.com/ubi9/ubi:9.0.0-1576

ENV LABEL=delete-me
ENV VALUE=true

COPY files/ /

WORKDIR /app

RUN yum install python3-devel -y && \
    yum clean all && \
    pip3 install --no-cache-dir --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /app/requirements.txt

CMD ["gunicorn", "--certfile=/certs/server.crt", "--keyfile=/certs/server.key", "--bind=0.0.0.0:8443", "wsgi:webhook"]
