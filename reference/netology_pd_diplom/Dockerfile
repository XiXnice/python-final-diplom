FROM python:3.9

# set work directory
WORKDIR /usr/src/netology_pd_diplom

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.dev.txt

# copy project
COPY . .