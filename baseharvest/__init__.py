from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from baseharvest.spiders.base_spider import BaseSpider



def run(urls):
    process = CrawlerProcess(get_project_settings())
    #spider.start_urls = ["http://hdl.handle.net/1885/10005"] #pass a new url to the spider
    BaseSpider.start_urls = urls
    process.crawl(BaseSpider)
    process.start()