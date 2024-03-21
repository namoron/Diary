FROM python:3.10.12
# 時刻設定
RUN cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
WORKDIR /app
COPY requirements.txt ./
RUN apt-get update -y
RUN apt-get upgrade -y
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run"]