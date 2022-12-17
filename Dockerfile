FROM python:3.11-alpine

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD [ "python3", "bot.py", "prod" ]