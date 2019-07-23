# -*- coding: utf-8 -*-
from news.items import NewsItem
import scrapy
import re
import time


class MoneydjSpider(scrapy.Spider):
    name = 'moneydj'
    allowed_domains = ['www.moneydj.com']
    start_urls = ['https://www.moneydj.com/KMDJ/News/NewsRealList.aspx?a=MB020000']
    default_url = 'https://www.moneydj.com'
    last_page = 1

    def parse(self, response):
        url = "https://www.moneydj.com/KMDJ/News/NewsRealList.aspx?a=MB020000"
        yield scrapy.Request(url=url, callback=self.parse_page)

    def parse_page(self, response):
        target = response.xpath('//table[@class="paging3"]/tr/td/a/@href')[-1].extract()
        self.logger.info("last page href: " + str(target))
        last_page = int(re.findall('index1=(\d+)', target)[0])

        for i in range(1, 10 if last_page > 10 else last_page):
            page_url = 'https://www.moneydj.com/KMDJ/News/NewsRealList.aspx?a=MB020000&index1=' + str(i)
            self.logger.info("page url: " + page_url)
            yield scrapy.Request(url=page_url, callback=self.parse_list)
            time.sleep(3)

    def parse_list(self, response):
        target = response.xpath('//*[@id="MainContent_Contents_sl_gvList"]/tr/td/a')

        for tag in target:
            try:
                url = tag.xpath('@href').extract_first()
                if url:
                    full_url = self.default_url + str(url)
                    self.logger.info(full_url)
                    yield scrapy.Request(url=full_url, callback=self.parse_context)
                    time.sleep(1)
            except IndexError:
                pass
            continue

    def parse_context(self, response):
        item = NewsItem()

        try:
            item['title'] = response.xpath('//span[@id="MainContent_Contents_lbTitle"]/text()').extract_first()
            item['author'] = response.xpath('//div[@id="highlight"]/article/p/text()').extract_first()
            item['date'] = response.xpath('//span[@id="MainContent_Contents_lbDate"]/text()').extract_first()
            item['content'] = response.xpath('//div[@id="highlight"]/article/text()').extract()
            return item
        except IndexError:
            pass
