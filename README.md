# baseharvest

Scrapy project for thesis harvesting. Harvests metadata from [BASE](http://base-search.net/).

- [baseharvest/spiders/base_spider.py](baseharvest/spiders/base_spider.py) is the spider which parses information from an BASE data XML file and follows links if necessary.

- [baseharvest/pipelines.py](baseharvest/pipelines.py) is the pipeline where scrapy writes the scraped items to an JSON file.

- [baseharvest/items.py](baseharvest/items.py) defines items where BASE data are stored.

- [Example input](recordi.xml), in BASE extended Dublin core metadata format.
- [Example output](jsons/butt_rachel_deborah_2013-05-09T05:16:48Z.json), in Inspire-friendly format.
