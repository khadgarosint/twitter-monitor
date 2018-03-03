import tweepy
import settings
import os
import rethinkdb as r

auth = tweepy.OAuthHandler(os.environ['TWITTER_OAUTH_KEY'], os.environ['TWITTER_OAUTH_SECRET'])
auth.set_access_token(os.environ['TWITTER_ACCESS_KEY'],
                      os.environ['TWITTER_ACCESS_SECRET'])



r.connect(os.environ.get('RETHINK_HOST', 'localhost'), int(os.environ.get('RETHINK_PORT', 28015))).repl()

class MyStreamListener(tweepy.StreamListener):

    def on_error(self, status_code):
        if status_code == 420:
            return False

    def on_status(self, status):
        terms = []
        for t in settings.TERMS:
            if t.lower() in status.text.lower():
                terms.append(t)
        print(status.text.lower())
        if terms:
            d = {'external_id': status.id_str, 'agent': 'twitter-monitor', 'source': status.source,
                 'text': status.text, 'type': 'tweet', 'sub_type': 'term-match',
                 'date': status.created_at.isoformat(), 'url': 'https://twitter.com/statuses/' + status.id_str,
                 'summary': status.text, 'terms': terms,
                 'metadata': {},
                 'tags': [], 'title': '', 'length': 0, 'author': status.user.name}

            if not r.db('khadgar').table('url').filter({'external_id': status.id_str}).count().run():
                r.db('khadgar').table('url').insert(d, conflict='update').run()


myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=auth, listener=myStreamListener)

track_terms = list(settings.TERMS)

myStream.filter(filter_level=None, track=track_terms)