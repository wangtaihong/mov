FROM python:2.7
RUN mkdir /web
WORKDIR E:/code/first
COPY . /web/
RUN pip install -r /web/requirements.txt
WORKDIR /web
#EXPOSE 8100
CMD [ "python", "./test.py" ]