import scrapy


class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://play.typeracer.com/']

    def parse(self, response: scrapy.Selector):
        for title in response.css('.oxy-post-title'):
            yield {'title': title.css('::text').get()}




