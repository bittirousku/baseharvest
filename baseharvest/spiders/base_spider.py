#!/usr/bin/python
# -*- coding: utf-8 -*-


#WHAT IF the ssl certificate of a https page is expired?? WON'T WORK
#exceptions.AttributeError: 'NoneType' object has no attribute 'failVerification'
#bug?
#http://stackoverflow.com/questions/30202669/nonetype-object-has-no-attribute-app-data-in-scrapy-twisted-openssl/30203408#30203408

from __future__ import print_function
from lxml import etree
import json
import os
import sys
import scrapy
from baseharvest.items import BaseDataItems
from scrapy import Request
import urllib 

    
class BaseSpider(scrapy.Spider):
    name = 'basespider' #spider name must be different from the project name!
    #start_urls = ["file:recordi.xml"]
    start_urls = []
    basedata = BaseDataItems()
       
    #custom_settings = {
        #'ITEM_PIPELINES': {'baseharvest.pipelines.BasePipeline': 100,} }
    
    #use this to pass arguments to spider, eg. the XML record filename
    #this should then be run like:
    #crapy crawl basespider -a file="file:recordi.xml"
    #look here: https://github.com/jalavik/harvest/blob/master/harvest/spiders/aps_spider.py
    def __init__(self, file=""):
        self.file = file
        self.start_urls = [file]

        
    #returns a list of element contents, can contain only one record
    #should the XML namespaces be removed?
    #This takes a scrapy response object.
    def get_base_element(self, response, el_name):
        xmlpath = "//*[local-name()='" + el_name  +"']/text()"
        elements = []
        for node in response.xpath(xmlpath):
            elements.append(node.extract())
        return elements
    
    #get mime type from url
    #Headers won't necessarily have 'Content-Type', so response.headers["Content-Type"] won't work
    #but for some reason this works??
    def get_mime_type(self, url):
        resp = urllib.urlopen(url)
        http_message = resp.info()
        print(http_message.type)
        return http_message.type
       
    
    #old but gold function to find the direct pdf link
    def find_pdf_link(self):
        print("Looking for the pdf url")
        print(self.start_urls)
        for link in self.start_urls: #start_urls should be defined before using this
            print(link)
            if "pdf" in self.get_mime_type(link): #MIME type
                print("Found direct link")
                return [ urllib.urlopen(link).geturl() ] #returns the possibly redirected url
            else:
                continue
        print("Didn't find direct link to PDF")  
        return []

    #this parses the domain from an url
    def parse_domain(self, url):
        from urlparse import urlparse
        parsed_uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        return domain
    
    #First parse the XML file and get the base data
    #and check if direct link exists
    def parse_xml_file(self, response):         
        #select scrapy response object and find the record
        hxs = scrapy.Selector(response)
        record = hxs.xpath("//*[local-name()='record']")
        #go through basedata and fill the Items
        for key in self.basedata.fields:
            self.basedata[key] = []
            self.basedata[key].extend( self.get_base_element(record, key) )
        
        self.basedata["doctype"] = ["PhD"] #This spider works now for PhDs
        #urls are either in identifier, relation or link XML element
        identifier = [el for el in self.basedata["identifier"] if "http" in el and "front" not in el.lower()]
        relation = [s for s in " ".join(self.basedata["relation"]).split() if "http" in s] #this element is messy
        link = self.basedata["link"]
        self.start_urls = list(set(identifier+relation+link))
        self.basedata["pdf_url"] = self.find_pdf_link()
        
    #Then make a new request with the splash page url we found or yield the base data
    def parse(self, response):         
        self.parse_xml_file(response)
        if not self.basedata["pdf_url"]:
            link = self.start_urls[0] #probably all links lead to same place #WHAT IF NOT??
            yield Request(link, callback = self.scrape_for_pdf)
        else: 
            yield self.basedata 

    
    #If no direct pdf link found, scrape the url
    def scrape_for_pdf(self, response):
        from urlparse import urljoin
        hxs = scrapy.Selector(response)
        all_links = hxs.xpath('*//a/@href').extract()
        #take only pdf-links, join relative urls with domain, and remove possible duplicates
        domain = self.parse_domain(response.url)
        all_links = sorted( list( set( [urljoin(domain, link) for link in all_links if "pdf" in link.lower() ] ) ) ) 
        #all_links = sorted( list( set( [urljoin(domain, link) for link in all_links ] ) ) ) #too slow to check them all!
        for link in all_links:
            #extract only links with pdf in them (checks also headers):
            if "pdf" in self.get_mime_type(link) or "pdf" in link.lower():
                self.basedata["pdf_url"].append( urljoin(domain, link) )
        #print(self.basedata)
        yield self.basedata



