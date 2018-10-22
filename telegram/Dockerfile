FROM "bitnami/python:2"
RUN pip install --upgrade pip
RUN pip install python-telegram-bot
RUN pip install requests
RUN pip install sparkworks==2.0.0
RUN pip install redis
COPY bot.py /app/bot.py
COPY utils.py /app/utils.py

CMD ["python","bot.py"]
