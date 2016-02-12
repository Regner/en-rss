

import os
import json
import logging
import urlparse
import requests
import feedparser

from time import sleep
from gcloud import datastore, pubsub

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# App Settings
SLEEP_TIME = int(os.environ.get('SLEEP_TIME', 300))
EN_RSS_SETTINGS_URL = os.environ.get('EN_RSS_SETTINGS_URL', 'http://en-rss-settings:8000/internal/')
SERVICES = [
    ('eve-news', 'http://newsfeed.eveonline.com/en-US/44/articles/page/1/20'),
    ('eve-blogs', 'http://newsfeed.eveonline.com/en-US/2/articles/page/1/20'),
    ('eve-dev-blogs', 'http://newsfeed.eveonline.com/en-US/95/articles'),
    ('cz', 'http://crossingzebras.com/feed/'),
    ('en24', 'http://evenews24.com/feed/'),
]

# Datastore Settings
DS_CLIENT = datastore.Client()
SERVICE_KIND = 'EN-RSS'

# PubSub Settings
PS_CLIENT = pubsub.Client()
PS_TOPIC = PS_CLIENT.topic(os.environ.get('NOTIFICATION_TOPIC', 'send_notification'))

if not PS_TOPIC.exists():
    PS_TOPIC.create()


def process_new_entry(feed, url, title):
    character_ids = get_characters(feed)
    
    if len(character_ids) > 0:
        send_notification(character_ids, title, url)
    
    else:
        logger.info('No subscribers for {}.'.format(feed))


def get_characters(feed):
    url = urlparse.urljoin(EN_RSS_SETTINGS_URL, feed)
    response = requests.get(url)
    response.raise_for_status()
    
    return response.json()
    

def send_notification(character_ids, title, url):
    logger.info('Publishing notification about {} for {} characters.'.format(title, len(character_ids)))
    character_ids_json = json.dumps(character_ids)
    
    PS_TOPIC.publish(
        title,
        url=url,
        service='en-rss',
        character_ids=character_ids_json,
    )


def update_latest_entry(feed, latest_entry, new_latest_entry):
    if latest_entry is None:
        latest_entry = datastore.Entity(DS_CLIENT.key(SERVICE_KIND, 'latest-entry', 'Feed', feed))
        latest_entry['published'] = new_latest_entry.published
        DS_CLIENT.put(latest_entry)

    if latest_entry['published'] != new_latest_entry.published:
        latest_entry['published'] = new_latest_entry.published
        DS_CLIENT.put(latest_entry)


while True:
    for feed, url in SERVICES:
        logger.info('Checking {} for new entries'.format(feed))
        feed_data = feedparser.parse(url)
        latest_entry = DS_CLIENT.get(DS_CLIENT.key(SERVICE_KIND, 'latest-entry', 'Feed', feed))

        for entry in feed_data.entries:
            if latest_entry is not None:
                if latest_entry['published'] == entry.published:
                    break

            converted_title = entry.title.encode('utf8')

            logger.info('New entry found for {}! Entry title: {}'.format(feed, converted_title))
            process_new_entry(feed, entry.link, converted_title)

        update_latest_entry(feed, latest_entry, feed_data.entries[0])

    sleep(SLEEP_TIME)
