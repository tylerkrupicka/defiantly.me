import tweepy
import nltk
import os
from keys import keys

CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_TOKEN = keys['access_token']
ACCESS_TOKEN_SECRET = keys['access_token_secret']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

"""
Django settings for defiantly project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0z(8$!p7j7sr&f#4nd_qs$o_m4u&w_ip1xi2a(bjtuq%-obp!&'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'defiantApp',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'defiantly.urls'

WSGI_APPLICATION = 'defiantly.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),}
    }

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

class Defiant:

    def __init__(self):
        #initialize class variables
        self.query = 'defiantly'
        self.record = 0
        self.recordHolder = " "
        self.corpusFile = "/home/django/defiantly/defiantly/corpus.txt"
        self.correctFile = "/home/django/defiantly/defiantly/correct.txt"
        self.incCorpus = []
        self.corCorpus = []
        self.taggedCorpus = []
        self.classifier = ""

    def main(self):
        print "loading corpus and creating classifier"
        self.createClassifier()
        return self.classifier

    def createData(self):
        #read incorrect corpus
        c = open(self.corpusFile)
        inc = c.readlines()
        c.close

        #remove special characters, users, and newlines
        for line in inc:
            #clean characters
            valid_chars = ' @abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            line = ''.join(c for c in line if c in valid_chars)
            line = line.strip()
            #save to incorrect corpus
            if len(line) != 0 and len(line) != 1:
                sp = line.split()
                if len(sp) == 0 or len(sp) == 1:
                    pass
                else:
                    self.incCorpus.append(sp)
            #remove user names
            for sentence in self.incCorpus:
                for word in sentence:
                    if word[0] == "@":
                        sentence.remove(word)

        #correct tweets
        c = open(self.correctFile)
        cor = c.readlines()
        c.close

        #remove special characters, users, and newlines
        for line in cor:
            #clean characters
            valid_chars = ' @abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            line = ''.join(c for c in line if c in valid_chars)
            line = line.strip()
            #save to incorrect corpus
            if len(line) != 0 and len(line) != 1:
                sp = line.split()
                if len(sp) == 0 or len(sp) == 1:
                    pass
                else:
                    self.corCorpus.append(sp)
            #remove user names
            for sentence in self.corCorpus:
                for word in sentence:
                    if word[0] == "@":
                        sentence.remove(word)

    def cleanText(self,text):
        valid_chars = ' @abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        text = ''.join(c for c in text if c in valid_chars)
        text = text.strip()
        #remove user names
        sent = text.split()
        for word in sent:
            if word[0] == "@":
                sent.remove(word)
        clean = " "
        return clean.join(sent)    

    def generateFeatures(self,tweet):
        index = 0
        features = {}
        #get index
        for i in range(0,len(tweet)):
            if tweet[i] == self.query:
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

    def createClassifier(self):
        self.createData()
        #create training corpus
        for tweet in self.incCorpus:
            self.taggedCorpus.append((self.generateFeatures(tweet),'incorrect'))
        for tweet in self.corCorpus:
            self.taggedCorpus.append((self.generateFeatures(tweet),'correct'))  

        self.classifier = nltk.NaiveBayesClassifier.train(self.taggedCorpus)

    def testClassifier(self):
        self.createClassifier()
        print "tested accuracy: " + str((nltk.classify.accuracy(self.classifier, self.taggedCorpus)))
        while True:
            phrase = ""
            phrase = raw_input("Enter Phrase to Classify: ")
            phrase = phrase.split()
            print phrase
            print self.classifier.classify(self.generateFeatures(phrase))

print os.path.dirname(os.path.abspath(__file__))
CLASSIFIER = Defiant().main()
print "completed"
