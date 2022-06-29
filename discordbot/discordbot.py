'''
Lit le tweet le mieux et le moins bien noté dans Postgres et envoie ces tweets a discordbot.
Garde la trace de la dernière heure à laquelle l'information a été obtenue, de sorte qu'à chaque itération, les tweets collectés au cours de la dernière heure sont interrogés.
dans la dernière heure sont interrogés
'''

import requests
import config
from sqlalchemy import create_engine
import time
import pandas as pd
import logging
import os

from discord import (
    Activity,
    ActivityType,
    Client,
    errors,
)
from datetime import datetime as dt

last_time = '2000-01-01 00:00:00'
#webhook init 
WEBHOOK = config.WEBHOOK


#POSTGRES INIT

HOST = 'postgres'
PORT = '5432'
USERNAME = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB = os.getenv("POSTGRES_DB")

conn_string = f'postgres://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}'
engine = create_engine(conn_string)





time.sleep(20) # dodo
while True: 

    query_worst = f"""
    SELECT timestamp, text, sentiment_score
    FROM   tweets
    WHERE  timestamp BETWEEN \'{last_time}\'::timestamp AND now()::timestamp
    ORDER BY sentiment_score LIMIT 1
    """

    query_best = f"""
    SELECT timestamp, text, sentiment_score
    FROM   tweets
    WHERE  timestamp BETWEEN \'{last_time}\'::timestamp AND now()::timestamp
    ORDER BY sentiment_score DESC LIMIT 1
    """
    
    # lire les queries et les assigner aux variables (tweet_worst et tweet_best)
    tweet_worst = pd.read_sql_query(query_worst, con=engine)
    tweet_best = pd.read_sql_query(query_best, con=engine)

    # last_time to current time
    last_time = str(pd.Timestamp.now())

    # valeur text et sentiment
    text_tweet_best = tweet_best['text'].iloc[0]
    sentiment_tweet_best =  tweet_best['sentiment_score'].iloc[0]
    
    text_tweet_worst = tweet_worst['text'].iloc[0]
    sentiment_tweet_worst =  tweet_worst['sentiment_score'].iloc[0]
    
    data = {
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Since the Last Update",
                
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Le meilleur tweet recu *\n:+1: score de : {sentiment_tweet_best}\n{text_tweet_best}"
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Le pire tweet recu*\n:-1: avec un score de : {sentiment_tweet_worst}\n{text_tweet_worst}"
            }
        }
    ]
}
    requests.post(url=WEBHOOK, json = data)

    time.sleep(60*60)         # sleep zZZZ