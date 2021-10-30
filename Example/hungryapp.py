import uuid
import re
import discord
import requests
from bs4 import BeautifulSoup
from requests.api import post


def get_latest_post(bcode):
    url = F'http://www.hungryapp.co.kr/bbs/list.php?bcode={bcode}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    soup = BeautifulSoup(requests.get(url, headers=headers).text, features="html.parser")
    row = soup.find('tr', attrs={'class':'deftr'})
    return HungryAppPost(row)


class HungryAppPost:
    def __init__(self, raw_post):
        self.author = raw_post.find('a', attrs={'class':'user'}).text
        self.title = raw_post.find('a', attrs={'class':'contt'}).find('font', {'color':''}).text
        self.timestamp = raw_post.find('span', attrs={'class':'time today'}).text

        post_id = raw_post.find('a', attrs={'class':'contt'})['href'].split('sendView(')[-1].split(',')[0]
        self.post_url = F'http://www.hungryapp.co.kr/bbs/bbs_view.php?pid={post_id}&bcode=honkai3rd&page=1'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        post_soup = BeautifulSoup(requests.get(self.post_url, headers=headers).text, features="html.parser")
        self.body = post_soup.find('div', attrs={'class':'bbs_cont contents'}).text
        self.body = re.sub(r'\n\s*\n', '\n\n', self.body)
        self.body = self.body[:4090]


        self.uuid = uuid.uuid5(uuid.NAMESPACE_DNS, F'{self.title}{self.author}{self.body}')
    
    def __str__(self):
        return F'Title: {self.title}\nBody: {self.body}\nAuthor: {self.author}\nTimestamp: {self.timestamp}\nUUID: {self.uuid}'

    @property
    def embed(self):
        embed=discord.Embed(
            title=F"{self.title} - {self.author}", 
            url=F"{self.post_url}", 
            description=F"{self.body}", 
            color=0xff9500
        )
        embed.set_author(name="헝그리앱 새 게시글", icon_url="http://appdata.hungryapp.co.kr/data_file/data_img/201906/14/W156049284205681175.png/hungryapp/resize/500")
        embed.set_footer(text=F"{self.timestamp}")
        return embed