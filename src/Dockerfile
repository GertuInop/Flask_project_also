FROM python:3.10-slim

RUN pip3 install --upgrade pip
RUN pip3 install --root-user-action=ignore requests
RUN pip3 install flask
RUN pip3 install flask_sqlalchemy
RUN pip3 install flask_login
RUN pip3 install werkzeug
RUN pip3 install datetime

ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /opt/app

COPY . /opt/app/

CMD [ "python", "./app.py" ]