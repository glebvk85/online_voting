FROM python:3.6
ADD . /OnlineVoting
WORKDIR /app
COPY runserver.py /app
COPY requirements.txt /app/requirements.txt
COPY OnlineVoting /app
COPY OnlineVoting.pyproj /app
RUN pip install -r requirements.txt
CMD ["python", "runserver.py"]
