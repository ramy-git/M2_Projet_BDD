'''
Tweet_Collector

Collecte les tweets de l'API Twitter à l'aide du StreamListener de la bibliothèque Tweepy.
Les tweets collectés sont écrits dans mongoDB.
Les informations d'identification de la base de données et de l'API sont lues dans ./config.py les personnes à suivre sont stockées dans ./infos.py
'''

import config
import infos
import pymongo
from tweepy import OAuthHandler, Stream
from tweepy.streaming import StreamListener
import json
import time

def organize_tweet(status):
    '''
Les tweets étendus et les retweets conservent l'affiche originale et le corps du tweet à différents endroits du tweet.
    Cette fonction de prétraitement renvoie le texte original du tweet et l'horodatage original.
    Elle indique également si le tweet a été retweeté et fournit des informations sur l'utilisateur qui l'a retweeté.
    '''

    
    if 'RT' not in status['text']:

        retweet = False
        rt_user = False
    
        if (status['truncated'] == False):
            tweet_text = status['text']
        else:
            tweet_text = status['extended_tweet']['full_text']
    else:

        try:

            retweet = True
            rt_user = status['retweeted_status']['user']['screen_name']

            if (status['retweeted_status']['truncated'] == False):
                tweet_text = status['retweeted_status']['text']
            else:
                tweet_text = status['retweeted_status']['extended_tweet']['full_text']
        
        except:

            retweet = False 
            rt_user = False
            tweet_text = status['text']
            
    
    return retweet, rt_user, tweet_text, status['created_at']


def authenticate():
    """
    Gère l'authentification de l'API Tweeter. Les informations d'identification doivent être stockées dans ./config.py.
    """
    auth = OAuthHandler(config.TW_API_KEY, config.TW_API_SECRET)
    auth.set_access_token(config.TW_ACC_TOKEN, config.TW_ACC_SECRET)

    return auth

class MaxTweetsListener(StreamListener):

    '''
    Hérite de StreamListener
    Définit on_connect, on_data, et on_error
    -> https://docs.tweepy.org/en/v3.2.0/streaming_how_to.html
    '''

    def __init__(self, max_tweets, *args, **kwargs):
        # initialize the StreamListener
        super().__init__(*args, **kwargs)
        # set the instance attributes
        self.max_tweets = max_tweets
        self.counter = 0
        self.tweet_list = []
        self.tweet_content = []

    def on_connect(self):
        '''
         En cas de connexion réussie
        '''
        print('connected. listening for incoming tweets')



    def on_data(self, data):
        """
        Traite le tweet lorsqu'il est intercepté. Le tweet est d'abord prétraité par organize_tweet().
        Ensuite, les informations requises sont extraites du tweet et écrites dans MongoDB.
        """
        status = json.loads(data)
      
        self.counter += 1

        retweet, rt_user, tweet_text, created_time = organize_tweet(status)   

        if status['user']['id_str'] in infos.twitterids:

            who = status['user']['id_str']

            try:
                replied_to = status['in_reply_to_screen_name']
            except:
                replied_to = 'NULL'
       
        else:
            
            who = status['user']['screen_name']
            
            try:
                replied_to = infos.twitterids[status['in_reply_to_user_id_str']]
            except:
                replied_to = 'NULL'
            
        tweet = {
            
            'id': status['user']['id_str'], #status.user.id_str,
            'who': who,
            'replied_to': replied_to,
            'retweeted': retweet, #status['retweeted'], #status.retweeted,
            'retweeted_from': rt_user,
            'text': tweet_text,
            'timestamp' : created_time
        }

        #ecrit dans MangoDB
        collection.insert_one(tweet)
        print(f'New tweet arrived: {tweet["text"]}')


        # cvérifier si nous avons assez de tweets collectés
        if self.max_tweets == self.counter:
            
            self.counter=0
            # retourne False pour arrêter le listener
            return False


    def on_error(self, status):
        if status == 420:
            print(f'Rate limit applies. Stop the stream.')
            return False

if __name__ == '__main__':

    while True:

        # Configurer la connexion mongoDB et obtenir la collection tweet.data
        client = pymongo.MongoClient("mongodb")
        db = client.tweets
        collection = db.tweet_data

        # Authentifier la connexion API et écouter les tweets (maximum 100 tweets par 5 minutes , possibilité de monter le nombre de tweet max selon le plan de l'API )
        auth = authenticate()
        listener = MaxTweetsListener(max_tweets=100)
        stream = Stream(auth, listener)

        # Filtrer les tweets pour ne retenir que ceux qui nous intéressent.
        follow = list(infos.people.values())
        stream.filter(follow=follow, languages=['en'], is_async=False)

        time.sleep(60*5)
    