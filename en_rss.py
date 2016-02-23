

import os
import json
import logging
import feedparser

from time import sleep
from gcloud import datastore, pubsub

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# App Settings
SLEEP_TIME = int(os.environ.get('SLEEP_TIME', 300))
SERVICES = {
    'eve-news': {
        'name': 'EVE Online News',
        'url': 'http://newsfeed.eveonline.com/en-US/44/articles/page/1/20',
        'official': True,
    },
    'eve-blogs': {
        'name': 'EVE Online Dev Blogs',
        'url': 'http://newsfeed.eveonline.com/en-US/2/articles/page/1/20',
        'official': True,
    },
    'eve-dev-blogs': {
        'name': 'EVE Online Developers Dev Blogs',
        'url': 'http://newsfeed.eveonline.com/en-US/95/articles',
        'official': True,
    },
    'cz': {
        'name': 'Crossing Zebras',
        'url': 'http://crossingzebras.com/feed/',
        'official': False,
    },
    'en24': {
        'name': 'EVE News 24',
        'url': 'http://evenews24.com/feed/',
        'official': False,
    },
}

# Datastore Settings
DS_CLIENT = datastore.Client()
SERVICE_KIND = 'EN-RSS'

# PubSub Settings
PS_CLIENT = pubsub.Client()
PS_TOPIC = PS_CLIENT.topic(os.environ.get('NOTIFICATION_TOPIC', 'send_notification'))

if not PS_TOPIC.exists():
    PS_TOPIC.create()


def send_notification(title, url, subtitle, feed_id):
    logger.info('Publishing notification about {}.'.format(title))
    
    topics = json.dumps(['/topics/{}'.format(feed_id)])
    
    PS_TOPIC.publish(
        '',
        url=url,
        title=title,
        subtitle=subtitle,
        service='en-rss',
        topics=topics,
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
    for feed_id in SERVICES:
        logger.info('Checking {} for new entries.'.format(feed_id))
        
        feed_url = SERVICES[feed_id]['url']
        feed_name = SERVICES[feed_id]['name']
        feed_data = feedparser.parse(feed_url)
        latest_entry = DS_CLIENT.get(DS_CLIENT.key(SERVICE_KIND, 'latest-entry', 'Feed', feed_id))

        for entry in feed_data.entries:
            if latest_entry is not None:
                if latest_entry['published'] == entry.published:
                    break

            converted_title = entry.title.encode('utf8')

            logger.info('New entry found for {}! Entry title: {}'.format(feed_id, converted_title))
            send_notification(feed_name, feed_url, converted_title, feed_id)

        update_latest_entry(feed_id, latest_entry, feed_data.entries[0])

    sleep(SLEEP_TIME)
