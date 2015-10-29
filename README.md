# baseharvest

Scrapy project for thesis harvesting. Harvests metadata from [BASE](http://base-search.net/)

- [baseharvest/spiders/base_spider.py](baseharvest/spiders/base_spider.py) is the spider which parses information from an BASE data XML file.

- [baseharvest/pipelines.py](baseharvest/pipelines.py) is the pipeline where scrapy writes the scraped items to an JSON file.

- [baseharvest/items.py](baseharvest/items.py) contains items where BASE data are stored.
