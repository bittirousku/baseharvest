# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import json
import os
import io

#Pipeline which takes the basedata items and writes them to a JSON file
class BasePipeline(object):
    #def __init__(self):
        #self.ids_seen = set()
        #outfile = 'items.json'
        #if os.path.exists(outfile):
            #os.remove(outfile)
        #self.file = open(outfile, 'wb')
    
    #check if language English and return True
    #language should be in JSON only if NOT English
    def is_eng(self, basedata):
        if basedata["language"]:
            if "en" in basedata["language"][0].lower():
                return True
            else:
                return False

    #find author(s):
    def get_author(self, basedata):
        if basedata["creator"]:
            return basedata["creator"] #author may be in "contributor":
        elif basedata["contributor"] and any("author" in contr.lower() for contr in basedata["contributor"]):  
            return [contr for contr in basedata["contributor"] if "author" in contr.lower()]
        else:
            return []
        
    #take author name and format it for filename use
    def format_author_name(self, author):
        return author.replace(",", "").replace(" ", "_").lower()
        
        
    #create a filename from the author name or timestamp
    def generate_outfile_name(self, basedata):
        try:
            out_filename = self.format_author_name(self.get_author(basedata)[0]) +"_"+ basedata["date"][0]
        except (IndexError, NameError):
            print("using datestamp as a filename")  
            out_filename = basedata["datestamp"][0].replace(":","_") #BASE datestamp
        except (IndexError, NameError):
            from time import strftime
            out_filename = strftime("%Y-%m-%d_%H_%M_%S") #local timestamp
        return out_filename
        
    #function to test the size of url list
    #(if multiple pdf links, probably no sense in downloading them all?)
    def multi_pdf_urls(self, pdf_url):
        if len(pdf_url) > 1:
            return True


    #download the PDF file
    def get_pdf_file(self, pdf_url, filename):
        print("getting the pdf file")
        import urllib2
        response = urllib2.urlopen(pdf_url[0])
        print("\taccessing...")
        pdf_content = response.read()
        f = open(filename+".pdf",'w')
        print("\twriting to file")
        f.write(pdf_content)
        f.close() 
        

    #count the number of pages in PDF file
    #when using, remember to check first whether 
    #the link contains a PDF and use the redirected url!!
    def get_no_pages(self, pdf_file, preserve):
        import pyPdf
        reader = pyPdf.PdfFileReader(open(pdf_file))
        if not preserve:
            #if you want to remove the file after accessing:
            os.remove(pdf_file)
        return reader.getNumPages()


    #this takes one item which contains a list and writes it to JSON.
    def process_item(self, item, spider):

        #nice to have the pdf url list as a variable:    
        pdf_url = item["pdf_url"]
        #also the author(s)
        authors = self.get_author(item)
        #and the outfilename:
        out_filename = self.generate_outfile_name(item)

        #print(item)

        #Finally create a JSON dictionary and dump it to a file
        print("Creating json dictionary")
        jsondic = {}

        if authors:
            jsondic["authors"]= [ {"name":author } for author in authors] #now supports multiple authors
        if item["title"]:
            jsondic["titles"] = [ {"title":title } for title in  item["title"]]
        if item["description"]:
            jsondic["abstracts"] = [ {"value":abstract } for abstract in item["description"]]
        if item["date"]:
            jsondic["thesis"] = [ {"date":item["date"][0], "degree_type":item["doctype"][0] } ]
        try:#this is ugly
            if item["language"]:
                if not self.is_eng(item):
                    jsondic["language"] = item["language"][0]
        except IndexError:
            pass
        if pdf_url: #do this only if some pdf link exists
            urlist = sorted( pdf_url + [el for el in item["identifier"] if "http" in el] ) #prob don't need "link" or "relation"
            if item["collname"]: #if there's a collection name, write that also
                collname = item["collname"][0]
                jsondic["url"] = [ {"url":url, "description": collname} for url in urlist if "pdf" not in url]
                jsondic["fft"] = [ {"url":url, "description": collname} for url in urlist if "pdf" in url]
            else:
                jsondic["url"] = [ {"url":url} for url in urlist if "pdf" not in url]
                jsondic["fft"] = [ {"url":url} for url in urlist if "pdf" in url]
            if not self.multi_pdf_urls(pdf_url): #count number of pages if only one pdf exists
                self.get_pdf_file(pdf_url, out_filename)
                jsondic["page_nr"] = self.get_no_pages(out_filename+".pdf", preserve=False)


        #write to file in unicode:
        print("Creating directories...")
        if not os.path.exists("jsons"):
            os.makedirs("jsons")

        print("Writing thesis '"+ jsondic["titles"][0]["title"] +"' metadata to file jsons/"+ out_filename+".json")
                
        with io.open("jsons/"+ out_filename+".json", 'w', encoding='utf-8') as f: 
            f.write(unicode(json.dumps(jsondic, ensure_ascii=False, indent=4)))



#What kind of problems should we except?