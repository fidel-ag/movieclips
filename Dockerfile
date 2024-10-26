FROM nas701/cybersec922-web5 
RUN apt install sqlite3 libsqlite3-dev -y
RUN apt install python3.10 -y
COPY requirements.txt /tmp/requirements.txt
RUN pip3.10 install --upgrade pip
RUN pip3.10 install -r /tmp/requirements.txt
WORKDIR /app
COPY . .
RUN python3.10  manage.py migrate
CMD python3.10  manage.py runserver

