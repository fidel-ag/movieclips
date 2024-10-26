FROM nas701/cybersec922-web5 
RUN apt install sqlite3 libsqlite3-dev -y
RUN apt-get update && \
    apt-get install -y wget build-essential \
    libssl-dev zlib1g-dev libncurses5-dev libnss3-dev libsqlite3-dev \
    libreadline-dev libffi-dev curl libbz2-dev && \
    rm -rf /var/lib/apt/lists/*
RUN wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz && \
    tar -xf Python-3.10.0.tgz && \
    cd Python-3.10.0 && \
    ./configure --enable-optimizations --enable-loadable-sqlite-extensions && \
    make && \
    make install && \
    cd .. && \
    rm -rf Python-3.10.0 Python-3.10.0.tgz
COPY requirements.txt /tmp/requirements.txt
RUN pip3.10 install --upgrade pip
RUN pip3.10 install -r /tmp/requirements.txt
WORKDIR /app
COPY . .
RUN python3.10  manage.py migrate
CMD python3.10  manage.py runserver

