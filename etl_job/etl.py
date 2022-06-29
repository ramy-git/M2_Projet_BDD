'''
Fonctionne toutes les 55 minutes
Il lit tout ce qui se trouve dans MongoDB, attribue un score de sentiment aux tweets et les transfère dans la db Postgres.
Puis se débarrasse de la collection MongoDB
Le timestamp utilisé est celui du tweet posté (du tweet original en cas de retweets).
'''
import os
import time
import pandas
import pymongo
import pandas as pd
import psycopg2
from pymongo import MongoClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sqlalchemy import create_engine


while True:
    #POSTGRES INIT

    HOST = 'postgres'
    PORT = '5432'
    USERNAME = os.getenv("POSTGRES_USER")
    PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB = os.getenv("POSTGRES_DB")

    conn_string = f'postgres://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    engine = create_engine(conn_string)

    #MONGODB INIT
    client = pymongo.MongoClient("mongodb")
    db = client.tweets
    collection = db.tweet_data


    #mongoDB en panda dataframe
    data = pd.DataFrame(list(collection.find()))
    #DROP la colonne _id 
    del data['_id']
    data['timestamp'] = pd.to_datetime(data['timestamp'])


    s = SentimentIntensityAnalyzer()
    data['sentiment_score'] = data['text'].apply(lambda x: x.replace('@','')).apply(lambda x: s.polarity_scores(x)['compound'])

    data.to_sql('tweets', engine, if_exists='append')

    client.drop_database('tweets')

    time.sleep(60*55)