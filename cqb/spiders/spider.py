import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import CqbItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class CqbSpider(scrapy.Spider):
	name = 'cqb'
	start_urls = ['https://www.ccbank.bg/bg/za-ckb/novini?page=1']

	def parse(self, response):
		post_links = response.xpath('//li[@class="news-list__item"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="paginator__btn paginator__btn--next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):

		date = response.xpath('//time/@datetime').get()
		date = re.findall(r'\d+\-\d+\-\d+',date)
		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//article[@class="text"]//text()[not (ancestor::time) and not (ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=CqbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		return item.load_item()
