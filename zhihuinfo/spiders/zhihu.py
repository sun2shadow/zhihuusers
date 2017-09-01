# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy import Request

from zhihuinfo.items import ZhihuinfoItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    start_user = 'excited-vczh'
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?incude={include}'
    user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    follow_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follow_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    follower_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}'
    follower_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'
    def start_requests(self):
        # url = 'https://www.zhihu.com/api/v4/members/corndog?include=allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), callback=self.parse_user)
        yield Request(self.follow_url.format(user=self.start_user, include=self.follow_query, offset=0, limit=20), callback=self.parse_follow)
        yield Request(self.follower_url.format(user=self.start_user, include=self.follower_query, offset=0, limit=20),callback=self.parse_follower)

    def parse_user(self, response):
        result = json.loads(response.text)
        item = ZhihuinfoItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item
        yield Request(self.follow_url.format(user=result.get('url_token'), include=self.follow_query, offset=0, limit=20), callback=self.parse_follow)
        yield Request(self.follower_url.format(user=result.get('url_token'), include=self.follower_query, offset=0, limit=20),callback=self.parse_follower)


    def parse_follow(self, response):
        results = json.loads(response.text)

        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query), callback=self.parse_user)
                if 'paging' in results.keys() and results.get('paging').get('id_end') == False:
                    next_page = results.get('paging').get('next')
                    yield Request(next_page, self.parse_follow)


    def parse_follower(self, response):
        results = json.loads(response.text)

        if 'data' in results.keys():
            for result in results.get('data'):
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query), callback=self.parse_user)
                if 'paging' in results.keys() and results.get('paging').get('id_end') == False:
                    next_page = results.get('paging').get('next')
                    yield Request(next_page, self.parse_follower)



