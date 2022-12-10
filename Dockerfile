FROM python:3.11

RUN pip install requests python-telegram-bot

ADD ConcertSetlistBot.py .
ADD conf.json .
ADD Config.py .
ADD help.html .
ADD Setlist.py .
ADD Stats.py .
ADD whatsnew.html .

CMD python3 ConcertSetlistBot.py