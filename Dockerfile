FROM python:3-alpine
WORKDIR /usr/src/app

RUN apk add --no-cache git
RUN git clone https://github.com/DrekkCuga/Winlink-GW.git /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]