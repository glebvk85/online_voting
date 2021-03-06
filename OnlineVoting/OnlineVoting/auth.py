
from uuid import uuid4
import urllib

trelloAuth = 'https://trello.com/1/authorize?'
appKey = '19f6350892758decb4ede6ae63be78b4'

def make_authorization_url(returnUrl):
	state = str(uuid4())
	params = {"expiration": "never",
			  "scope": "read,write,account",
			  "response_type": "token",
			  "name": "Server Token",
			  "key": appKey,
			  "return_url": returnUrl}
	url = trelloAuth + urllib.parse.urlencode(params)
	return url

