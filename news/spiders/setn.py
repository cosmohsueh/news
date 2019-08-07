# -*- coding: utf-8 -*-
from news.items import NewsItem
import scrapy
import re
import time


class SetnSpider(scrapy.Spider):
    name = 'setn'
    allowed_domains = ['www.setn.com']
    start_urls = ['https://www.setn.com/ViewAll.aspx?PageGroupID=2']
    default_url = 'https://www.setn.com/'
    last_page = 1

    def parse(self, response):
        url = "https://www.setn.com/search.aspx?q=%E4%BF%9D%E9%9A%AA"
        yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        target = response.xpath('//*[@id="aspnetForm"]/div/div/div/div/div/ul/li/a/@href')[-1].extract()
        self.logger.info("last page href: " + str(target))
        last_page = re.findall('p=(\d+)', target)[0]

        for i in range(1, 2):
            page_url = 'https://www.setn.com/search.aspx?q=%E4%BF%9D%E9%9A%AA&p=' + str(i)
            self.logger.info("find page url: " + page_url)
            yield scrapy.Request(url=page_url, callback=self.parse_list)
            time.sleep(3)

    def parse_list(self, response):
        target = response.xpath('//*[@id="aspnetForm"]/div/div/div/div/div/div/a')

        for tag in target:
            try:
                url = tag.xpath('@href').extract_first()
                if url:
                    full_url = self.default_url + str(url)
                    self.logger.info("content page url:" + full_url)
                    yield scrapy.Request(url=full_url, callback=self.parse_context)
                    time.sleep(1)
            except IndexError:
                pass
            continue

    def parse_context(self, response):
        item = NewsItem()

        try:
            item['title'] = response.xpath('//*[@id="contFix"]/div/div[2]/h1/text()').extract_first()
            item['author'] = response.xpath('//*[@id="contFix"]/div/div[2]/div[3]/div[1]/span/text()').extract_first()
            item['date'] = response.xpath('//*[@id="contFix"]/div/div[2]/div[3]/div[1]/time/text()').extract_first()
            item['content'] = response.xpath('//*[@id="Content1"]').extract_first()
            item['channel'] = '三立'
            item['url'] = response.request.url
            return item
        except IndexError:
            pass
