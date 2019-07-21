# -*- coding: utf-8 -*-
from news.items import NewsItem
import scrapy
import re
import time


class SetnSpider(scrapy.Spider):
    name = 'setn'
    allowed_domains = ['www.setn.com']
    start_urls = ['https://www.setn.com/ViewAll.aspx?PageGroupID=2']
    default_url = 'https://www.setn.com'
    last_page = 1

    def parse(self, response):
        url = "https://www.setn.com/ViewAll.aspx?PageGroupID=2"
        yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        target = response.xpath('//*[@id="contFix"]/div/div/div/div/div/ul/li/a/@href')[-1].extract()
        last_page = re.findall('p=(\d+)', target)[0]

        for i in range(1, int(last_page)):
            page_url = 'https://www.setn.com/ViewAll.aspx?PageGroupID=2&p=' + str(i)
            yield scrapy.Request(url=page_url, callback=self.parse_list)
            time.sleep(3)

    def parse_list(self, response):
        target = response.xpath("//*[@id='contFix']/div/div/div/div")

        for tag in target:
            try:
                url = tag.xpath('div/h3/a/@href').extract_first()
                if url:
                    full_url = self.default_url + str(url)
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
            print(item)
        except IndexError:
            pass
