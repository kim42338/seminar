import json
import uuid

import boto3
import requests
from bs4 import BeautifulSoup
from chalice import Chalice, Rate

app = Chalice(app_name='notification')


def get_dc_post(*, gallery_id):
    host = 'https://gall.dcinside.com'
    resource = '/mgallery/board/lists'
    headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
    params = {
        'id': gallery_id,
        'sort_type': 'N',
        'page': '1'
    }
    html = requests.get(host + resource, params=params, headers=headers)
    board = BeautifulSoup(html.content, 'html.parser')
    post_soup = board.find('table', {'class': 'gall_list'}) \
                .find('tbody') \
                .find('tr', attrs={'class': 'ub-content us-post', 'data-type': lambda x: x in ['icon_pic', 'icon_txt']})
    title_soup = post_soup.find('a', href=True)
    title = title_soup.text
    url = host + title_soup['href']
    date_soup = post_soup.find('td', attrs={'class': 'gall_date'})
    date = date_soup['title']

    post = {
        'title': title,
        'date': date,
        'url': url
    }
    return post


def format_slack_message(**kwargs):
    text = ''
    for k, v in kwargs.items():
        text += F'{v}\n'
    return {'text': text}


def send_slack_message(slack_message):
    webhook_url = 'https://hooks.slack.com/services/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'
    requests.post(webhook_url, data=json.dumps(slack_message))


@app.schedule(Rate(1, unit=Rate.MINUTES))
def periodic_task(event):
    s3_client = boto3.client('s3')
    new_dc_post = get_dc_post(gallery_id='ipad1')
    post_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, new_dc_post['title']))
    try:
        uuid_obj = s3_client.get_object(
            Bucket='notification-uuid-bucket',
            Key='uuid'
        )
        last_uuid = uuid_obj['Body'].read().decode('utf-8')
    except:
        last_uuid = None
    print(F'post:{post_uuid} last:{last_uuid}')
    if post_uuid != last_uuid:
        formatted_message = format_slack_message(**new_dc_post)
        print(F'new post detected: {formatted_message}')
        send_slack_message(formatted_message)
        s3_client.put_object(
            Bucket='notification-uuid-bucket',
            Key='uuid',
            Body=F'{str(post_uuid)}'.encode('utf-8')
        )