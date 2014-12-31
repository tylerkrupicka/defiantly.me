from django.shortcuts import render, render_to_response, RequestContext, HttpResponseRedirect
from models import *
from django.conf import settings
import tweepy
import nltk
from keys import keys

CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_TOKEN = keys['access_token']
ACCESS_TOKEN_SECRET = keys['access_token_secret']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
query = 'defiantly'

classifier = settings.CLASSIFIER
# Create your views here.
def index(request):
    #clear tweets array
    tweets = pollForTweets()
    for tweet in tweets:
        if(badTweet.objects.filter(tweetId=tweet.id).exists()):
            pass
        else:
            bad = badTweet(tweetId=tweet.id,user=tweet.user.screen_name,followers=tweet.user.followers_count,tweetText=tweet.text)
            bad.save()
    tweetNum = len(badTweet.objects.all())
    badTweets = badTweet.objects.order_by('-followers', 'tweetId')[:10]
    return render(request, "index.html", locals())



def pollForTweets():
    #add the current pulling tweets with lowered text
    #to the array for processing for the next post
    tweets = []
    print "polling!"
    try:
        currentPoll = [status for status in tweepy.Cursor(api.search, q=query).items(20)]
    except tweepy.TweepError, e:
        print 'poll failed because of %s' % e.reason

    for tweet in currentPoll:
        tweet.text = tweet.text.lower()
        clean = tweet.text
        clean = clean.split()

        if classifier.classify(generateFeatures(clean)) == 'correct':
            pass
        elif hasattr(tweet, 'retweeted_status'):
            pass
        elif "rt @" in tweet.text or " rt " in tweet.text:
            pass
        elif "difference" in tweet.text or "spell" in tweet.text:
            pass
        elif "definitely" in tweet.text:
            pass
        else:
            tweets.append(tweet)
    return tweets

def generateFeatures(tweet):
        index = 0
        features = {}
        #get index
        for i in range(0,len(tweet)):
            if tweet[i] == query:
                index = i
        pos = nltk.pos_tag(tweet)
        #previous word feature
        if index != 0:
            previousWord = tweet[index-1]
            token = pos[index-1]
            features['previousWord'] = previousWord
            #previous letter
            features['previousWordEndL'] = previousWord[-1]
            features['previousWordPos'] = token[1]
        else:
            features['previousWord'] = "none"
            features['previousWordEndL'] = "none"
            features['previousWordPos'] = "none"
        
        #next word feature
        if index < len(tweet)-1:
            #print str(index) + " " + str(len(tweet))
            nextWord = tweet[index + 1]
            token = pos[index+1]
            features['nextWord'] = nextWord
            features['nextWordEndL'] = nextWord[-1]
            features['nextWordPos'] = token[1]
        else:
            features['nextWord'] = "none"
            features['nextWordEndL'] = "none"
            features['nextWordPos'] = "none"

        return features