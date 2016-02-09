

import os
import pytz
import logging
import feedparser

from time import mktime, sleep
from gcloud import datastore, pubsub
from datetime import datetime

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# App Settings
SERVICE_ID = os.environ.get('SERVICE_ID', 'EN-RSS-EVE') 
FEED = os.environ.get('FEED_URL', 'http://newsfeed.eveonline.com/en-US/2/articles/page/1/20')                                                                                                                                               
SLEEP_TIME = int(os.environ.get('SLEEP_TIME', 300))

# Datastore Settings
DS_CLIENT = datastore.Client()
SERVICE_KIND = os.environ.get('DATASTORE_SERVICE_KIND', SERVICE_ID)
SETTINGS_KIND = os.environ.get('DATASTORE_SETTINGS_KIND', 'EN-SETTINGS')

# PubSub Settings
PS_CLIENT = pubsub.Client()
PS_TOPIC = PS_CLIENT.topic(os.environ.get('NOTIFICATION_TOPIC', 'send_notification'))

if not PS_TOPIC.exists():
    PS_TOPIC.create()


def process_new_entry(url, title):
    character_ids = get_characters()
    send_notification(character_ids, title, url)


def get_characters():
    query = DS_CLIENT.query(kind=SETTINGS_KIND)
    query.add_filter('service', '=', SERVICE_ID)
    return [x['id'] for x in query.fetch()]
    

def send_notification(character_ids, title, url):
    PS_TOPIC.publish(
        message=title,
        service=SERVICE_ID,
        url=url,
        character_ids=character_ids
    )


def update_latest_entry(latest_entry, new_latest_entry):
    if latest_entry is None:
        latest_entry = datastore.Entity(DS_CLIENT.key(SERVICE_KIND, 'latest-entry'))

    latest_entry['published'] = new_latest_entry.published
    DS_CLIENT.put(latest_entry)


while True:
    logger.info('Checking {} for new entries'.format(SERVICE_ID))
    feed_data = feedparser.parse(FEED)
    latest_entry = DS_CLIENT.get(DS_CLIENT.key(SERVICE_KIND, 'latest-entry'))

    for entry in feed_data.entries:
        if latest_entry is not None:
            if latest_entry['published'] == entry.published:
                break

        converted_title = entry.title.encode('utf8')

        logger.info('New entry found for {}! Entry title: {}'.format(SERVICE_ID, converted_title))
        process_new_entry(entry.url, converted_title)

    update_latest_entry(latest_entry, feed_data.entries[0])

    sleep(SLEEP_TIME)

