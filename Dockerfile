FROM nas701/cybersec922-web5 
RUN apt install libsqlite3-dev
COPY requirements.txt /tmp/requirements.txt
RUN pip3.10 install -r /tmp/requirements.txt
WORKDIR /app
COPY . .
RUN python3.10  manage.py migrate
CMD python3.10  manage.py runserver

