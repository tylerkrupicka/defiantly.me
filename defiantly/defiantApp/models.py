from django.db import models

# Create your models here.
class badTweet(models.Model):

	tweetId = models.CharField(max_length=255)
	user = models.CharField(max_length=255)
	followers = models.IntegerField(max_length=15)
