

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
EN_RSS_SETTINGS_URL = os.environ.get('EN_RSS_SETTINGS_URL', 'http://en-rss-settings:8000/')

# Datastore Settings
DS_CLIENT = datastore.Client()
SERVICE_KIND = 'EN-RSS'

# PubSub Settings
PS_CLIENT = pubsub.Client()
PS_TOPIC = PS_CLIENT.topic(os.environ.get('NOTIFICATION_TOPIC', 'send_notification'))

if not PS_TOPIC.exists():
    PS_TOPIC.create()


def process_new_entry(feed_id, feed_name, url, title):
    character_ids = get_characters(feed_id)
    
    if len(character_ids) > 0:
        send_notification(character_ids, title, url, feed_name, feed_id)
    
    else:
        logger.info('No subscribers for {} so not publishing message for {}.'.format(feed, title))


def get_characters(feed):
    url = urlparse.urljoin(EN_RSS_SETTINGS_URL, 'internal', feed)
    response = requests.get(url)
    response.raise_for_status()
    
    return response.json()


def get_services():
    url = urlparse.urljoin(EN_RSS_SETTINGS_URL, 'external')
    response = requests.get(url)
    response.raise_for_status()
    
    return response.json()

def send_notification(character_ids, title, url, feed_name, feed_id):
    logger.info('Publishing notification about {} for {} characters.'.format(title, len(character_ids)))
    character_ids_json = json.dumps(character_ids)
    
    PS_TOPIC.publish(
        title,
        url=url,
        feed_name=feed_name,
        service='en-rss',
        character_ids=character_ids_json,
        collapse_key=feed_id,
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
    services = get_services()
    logger.info('Got the following service definitions: {}'.format(services))
    
    for feed_id in services:
        feed_url = services[feed_id]['url']
        feed_name = services[feed_id]['name']
        
        logger.info('Checking {} for new entries.'.format(feed_id))
        feed_data = feedparser.parse(feed_url)
        latest_entry = DS_CLIENT.get(DS_CLIENT.key(SERVICE_KIND, 'latest-entry', 'Feed', feed_id))

        for entry in feed_data.entries:
            if latest_entry is not None:
                if latest_entry['published'] == entry.published:
                    break

            converted_title = entry.title.encode('utf8')

            logger.info('New entry found for {}! Entry title: {}'.format(feed_id, converted_title))
            process_new_entry(feed_id, feed_name, entry.link, converted_title)

        update_latest_entry(feed_id, latest_entry, feed_data.entries[0])

    sleep(SLEEP_TIME)
