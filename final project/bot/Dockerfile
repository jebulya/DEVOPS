FROM python:3.11.2

WORKDIR /code

COPY bot/requirements.txt .

RUN pip install -r requirements.txt

COPY bot/bot.py .

COPY .env .

CMD [ "python", "./bot.py" ]