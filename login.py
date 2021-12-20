#Use this on your desktop to login one time (it will open a browser), and it will create the credentials.storage file

from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo

# loggin into the channel
channel = Channel()
channel.login("client_secret.json", "credentials.storage")
