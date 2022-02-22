FROM python:3.8


WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY ./requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .

RUN pyppeteer-install 

# pyppeteer required libs
RUN apt update && apt-get install -y libxshmfence-dev libdrm-dev libgbm-dev libpangocairo-1.0-0 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 libxi6 libxtst6 libnss3 libcups2 libxss1 libxrandr2 libasound2 libatk1.0-0 libgtk-3-0

COPY . .


CMD [ "./entrypoint.sh" ]