

import os
import json
import logging
import requests
import feedparser

from time import sleep
from gcloud import datastore, pubsub

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# App Settings
SLEEP_TIME = int(os.environ.get('SLEEP_TIME', 300))
EN_TOPIC_SETTINGS = os.environ.get('EN_TOPIC_SETTINGS', 'http://en-topic-settings:80/external')

# Datastore Settings
DS_CLIENT = datastore.Client()
SERVICE_KIND = 'EN-RSS'

# PubSub Settings
PS_CLIENT = pubsub.Client()
PS_TOPIC = PS_CLIENT.topic(os.environ.get('NOTIFICATION_TOPIC', 'send_notification'))

if not PS_TOPIC.exists():
    PS_TOPIC.create()


def send_notification(title, url, subtitle, feed_id):
    topics = json.dumps([feed_id])
    
    PS_TOPIC.publish(
        '',
        url=url,
        title=title,
        subtitle=subtitle,
        service='en-rss',
        topics=topics,
    )


def get_services():
    response = requests.get(EN_RSS_SETTINGS_URL)
    response.raise_for_status()

    return response.json()['rss']['topics']


def update_latest_entry(feed, latest_entry, new_latest_entry):
    if latest_entry is None:
        latest_entry = datastore.Entity(DS_CLIENT.key(SERVICE_KIND, 'latest-entry', 'Feed', feed))
        latest_entry['published'] = new_latest_entry.published
        DS_CLIENT.put(latest_entry)

    if latest_entry['published'] != new_latest_entry.published:
        latest_entry['published'] = new_latest_entry.published
        DS_CLIENT.put(latest_entry)


while True:
    services = get_services()
    
    for feed in services:
        logger.info('Checking "{}" for new entries.'.format(feed['name']))

        feed_data = feedparser.parse(feed['url'])
        latest_entry = DS_CLIENT.get(DS_CLIENT.key(SERVICE_KIND, 'latest-entry', 'Feed', feed['topic']))
        
        if 'bozo_exception' in feed_data:
            logger.info('Bozo exception "{}" when trying to fetch {}'.format(feed_data['bozo_exception'], feed['url']))

        for entry in feed_data.entries:
            if latest_entry is not None:
                if latest_entry['published'] == entry.published:
                    break

            converted_title = entry.title.encode('utf8')

            logger.info('New entry found for "{}"! Entry title: {}'.format(feed['name'], converted_title))
            send_notification(feed['name'], feed['url'], converted_title, feed['topic'])

        if len(feed_data.entries) > 0:
            update_latest_entry(feed['topic'], latest_entry, feed_data.entries[0])

    sleep(SLEEP_TIME)
