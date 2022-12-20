FROM python:3.10-alpine
#supabase 3:11 has errors with supabase

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD [ "python3", "bot.py", "prod" ]