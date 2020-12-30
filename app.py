import os
from flask import render_template, request, json
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from Tweets import create_app
from collections import Counter
from textblob import TextBlob
import operator

config_name = os.getenv('FLASK_CONFIG', 'development')
app = create_app(config_name)

ckey = "xDHW87silQGmPgtEgE2M1wWdp"
csecret = "lTt3WgG9dHj6IdIadGDCB1SHGe3KtDzhe0xT0yeWkhDgntTojE"
atoken = "1342146790976487431-fHbYzoQHHybPuIT3XUwqyJlIIJda21"
asecret = "dngthM03Sh1b4t7bi999pt83DM9HEKAE1wxSWCw2AfXzy"


@app.route('/', methods=['GET', 'POST'])
def twt_search():
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        tweets = []
        lst_tweets = []

        class Listener(StreamListener):
            def on_data(self, data):
                json_load = json.loads(data)
                dict_tweets = dict()
                for i in json_load:
                    analysis = TextBlob(json_load["text"])
                    print(analysis.sentiment)
                    if analysis.sentiment[0] > 0:
                        dict_tweets['sentiment'] = "Positive"
                    elif analysis.sentiment[0] < 0:
                        dict_tweets['sentiment'] = "Negative"
                    else:
                        dict_tweets['sentiment'] = "Neutral"

                    dict_tweets["created_at"] = json_load["created_at"]
                    dict_tweets["text"] = json_load["text"]
                    dict_tweets["favourites_count"] = json_load["user"]["favourites_count"]
                    dict_tweets["followers_count"] = json_load["user"]["followers_count"]
                    dict_tweets["friends_count"] = json_load["user"]["friends_count"]
                    dict_tweets["profile_image_url_https"] = json_load["user"]["profile_image_url_https"]
                    dict_tweets["retweet_count"] = json_load.get('retweeted_status', {}).get('retweet_count',
                                                                                       json_load.get('quoted_status',
                                                                                                     {}).get(
                                                                                           'retweet_count'))

                lst_tweets.append(dict_tweets)
                tweets.append(json_load['text'])

                if len(tweets) == 10:
                    return False
                return True

        keyword = request.form.get('keyword')

        auth = OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)

        twitterstream = Stream(auth, Listener())
        twitterstream.filter(languages=['en'], track=[keyword])

        lst_words = []
        for i in tweets:
            lst_words += i.split()
        dict_twt_word = Counter(lst_words)
        del dict_twt_word["RT"]
        del dict_twt_word[keyword]
        word = max(dict_twt_word.items(), key=operator.itemgetter(1))[0]

        return render_template('tweet.html', tweets=lst_tweets, word=word)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
