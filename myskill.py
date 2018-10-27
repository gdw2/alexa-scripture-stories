from flask import Flask
from flask_ask import Ask, statement, audio, current_stream
import podcastparser
import urllib.request
import random
import json
import logging
import requests

app = Flask(__name__)
ask = Ask(app, '/')

logger = logging.getLogger()
logging.getLogger('flask_ask').setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG)

@ask.launch
def play():
    feedurl = 'http://feeds.lds.org/ScriptureStories'
    parsed = podcastparser.parse(feedurl, urllib.request.urlopen(feedurl))
    episode = random.choice(parsed['episodes'])
    url = episode['enclosures'][0]['url']
    url = requests.get(url, allow_redirects=False).headers['location']
    url = url.replace('http','https')
    speech = f"Playing Scripture Story {episode['title']}"
    _infodump(f"{speech} ({url})")
    return audio(speech).play(url)#, offset=93000)

@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio('Paused the stream.').stop()


@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio('Resuming.').resume()

@ask.intent('AMAZON.StopIntent')
def stop():
    return audio('stopping').clear_queue(stop=True)

# optional callbacks
@ask.on_playback_started()
def started(offset, token):
    _infodump('STARTED Audio Stream at {} ms'.format(offset))
    _infodump('Stream holds the token {}'.format(token))
    _infodump('STARTED Audio stream from {}'.format(current_stream.url))


@ask.on_playback_stopped()
def stopped(offset, token):
    _infodump('STOPPED Audio Stream at {} ms'.format(offset))
    _infodump('Stream holds the token {}'.format(token))
    _infodump('Stream stopped playing from {}'.format(current_stream.url))


@ask.on_playback_nearly_finished()
def nearly_finished():
    _infodump('Stream nearly finished from {}'.format(current_stream.url))

@ask.on_playback_finished()
def stream_finished(token):
    _infodump('Playback has finished for stream with token {}'.format(token))

@ask.session_ended
def session_ended():
    return "{}", 200

def _infodump(obj, indent=2):
    msg = json.dumps(obj, indent=indent)
    logger.info(msg)

if __name__ == '__main__':
    app.run()
