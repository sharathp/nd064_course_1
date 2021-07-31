FROM python:2.7

COPY . /app
WORKDIR /app

# expose port
EXPOSE 3111

# install dependencies
RUN pip install -r requirements.txt

# bootstrap database
RUN python init_db.py

# command to run on container start
CMD [ "python", "app.py" ]
