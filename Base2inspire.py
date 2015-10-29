#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from lxml import etree
import json
import os
import sys

#BASE XML-file of records to JSON files of individual records
#this is now just a test
#tree = etree.parse("testi_base.xml")
#the functions take only one record at a time,
#not the whole tree (ie not the whole xml file of records)


#recno = int(sys.argv[1])

#this takes the file containing records
#tree = etree.parse("oai.xml")
tree = etree.parse("recordi.xml") #tätä testataan nytten


records = tree.xpath("//*[local-name()='record']") #list of elements (records)
record = records[0]#take one record for testing




#returns a list of element contents, can contain only one record
#should the XML namespaces be removed?
def get_base_element(tree, el_name):
    xmlpath = ".//*[local-name() =   '" + el_name  +"']" 
    elements = []
    for node in tree.xpath(xmlpath):
        elements.append(node.text)
    
    return elements


#python dic containing data extracted from BASE xml metadata
#final output should be JSON!
basedata = {'creator':[],
            'title':[],
            'description':[], 
            'language':[], 
            'date':[],
            'type':[],
            'classcode':[], 
            'autoclasscode':[],
            'collname':[],
            'identifier':[],
            'typenorm':[],
            'contributor':[],
            'year':[],
            'datestamp':[]
            }

#iterate through the dic and fill it with BASE data
print("generating basedata dictionary from XML file ")
for key in basedata:
    basedata[key].extend( get_base_element(record, key) )



#check if record is a phd
#don't need this
#def is_phd(basedata):
    #if basedata["typenorm"][0]=="0004":
        #return True
    #elif any("thesis" in doctype for doctype in basedata["type"]):
        #return True
    #else:
        #return False
        


#check if language English and return True
#language should be in JSON only if NOT English
def is_eng(basedata):
    if basedata["language"]:
        if "en" in basedata["language"][0].lower():
            return True
        else:
            return False


#check if subject is physics
#don't need this
#def is_physics(basedata):
    #if "53" in basedata["classcode"]:
        #return True
    #else:
        #return False


#find author(s):
def get_author(basedata):
    if basedata["creator"]:
        return basedata["creator"] #author may be in "contributor":
    elif basedata["contributor"] and any("author" in contr.lower() for contr in basedata["contributor"]):  
        return [contr for contr in basedata["contributor"] if "author" in contr.lower()]
    else:
        return []
    
#take author name and format it for filename use
def format_author_name(author):
    return author.replace(",", "").replace(" ", "_").lower()
    
    
#create a filename from the author name or timestamp
def generate_outfile_name(basedata):
    try:
        out_filename = format_author_name(get_author(basedata)[0]) +"_"+ basedata["date"][0]
    except (IndexError, NameError):
        print("using datestamp as a filename")  
        out_filename = basedata["datestamp"][0].replace(":","_") #BASE datestamp
    except (IndexError, NameError):
        from time import strftime
        out_filename = strftime("%Y-%m-%d_%H_%M_%S") #local timestamp
    return out_filename



#The actual scraping function that magically works!
#run() is in project file __init__.py
def scrape_pdf_url(basedata):
    urls = [el for el in basedata["identifier"] if "http" in el and "front" not in el.lower()] #pdf link might be front page only
    from baseharvest import run
    run(urls[:1]) #probably won't need to check all the pages...anyway code breaks now if it does :) has to be a list!
    print("scraping finished")


#check which link contains a PDF file
#if no pdf link present, run the scrape_pdf_url function
#which uses scrapy to follow links and find the pdf url
def find_pdf_link(basedata):
    import urllib #for some reason urllib2 doesn't work???
    print("Looking for the pdf url")
    urls = [el for el in basedata["identifier"] if "http" in el and "front" not in el.lower()]
    print(urls)
    for url in urls:
        response = urllib.urlopen(url)
        http_message = response.info()
        print(http_message.type)
        if "pdf" in http_message.type: #MIME type
            print("Found direct link")
            return [ response.geturl() ] #returns the possibly redirected url
        else:
            continue
    print("Didn't find direct link, trying to scrape next")
    #return []
    print("scraping the page for pdf url...")
    scrape_pdf_url(basedata)
    #print("opening json file")
    url_json_file = open("items.json", "r")
    #print("file opened")
    pdf_url_dic = json.load(url_json_file) #this doesn't work if the spider didn't close the file properly....
    #print("json loaded")
    url_json_file.close()
    os.remove("items.json")
    return pdf_url_dic["pdf_url"] #this will contain the scraped pdf url(s) as a list



#function to test the size of url list
#(if multiple pdf links, probably no sense in downloading them all?)
def multi_pdf_urls(pdf_url):
    if len(pdf_url) > 1:
        return True


#download the PDF file
def get_pdf_file(pdf_url, filename):
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
#when using, remember to check first wheter 
#the link contains a PDF and use the redirected url!!
def get_no_pages(pdf_file, preserve):
    import pyPdf
    reader = pyPdf.PdfFileReader(open(pdf_file))
    if not preserve:
        #if you want to remove the file after accessing:
        os.remove(pdf_file)
    return reader.getNumPages()





#nice to have the pdf url list as a variable:    
pdf_url = find_pdf_link(basedata)
#also the author(s)
authors = get_author(basedata)
#and the outfilename:
out_filename = generate_outfile_name(basedata)



#Finally create a JSON dictionary and dump it to a file
print("Creating json dictionary")
jsondic = {}

if authors:
    jsondic["authors"]= [ {"name":author } for author in authors] #supports multiple authors
if basedata["title"]:
    jsondic["titles"] = [ {"title":title } for title in  basedata["title"]]
if basedata["description"]:
    jsondic["abstracts"] = [ {"value":abstract } for abstract in basedata["description"]]
if basedata["date"]:
    jsondic["thesis"] = [ {"date":basedata["date"][0], "degree_type":"PhD" } ]
try:#this is ugly
    if basedata["language"]:
        if not is_eng(basedata):
            jsondic["language"] = basedata["language"][0]
except IndexError:
    pass
if pdf_url: #do this only if some pdf link exists
    urlist = sorted( pdf_url + [el for el in basedata["identifier"] if "http" in el] )
    if basedata["collname"]: #if there's a collection name, write that also
        collname = basedata["collname"][0]
        jsondic["url"] = [ {"url":url, "description": collname} for url in urlist if "pdf" not in url]
        jsondic["fft"] = [ {"url":url, "description": collname} for url in urlist if "pdf" in url]
    else:
        jsondic["url"] = [ {"url":url} for url in urlist if "pdf" not in url]
        jsondic["fft"] = [ {"url":url} for url in urlist if "pdf" in url]
    if not multi_pdf_urls(pdf_url): #count number of pages if only one pdf exists
        get_pdf_file(pdf_url, out_filename)
        jsondic["page_nr"] = get_no_pages(out_filename+".pdf", preserve=False)



print("Creating directories...")
#write to file in unicode:
import io, json, os
if not os.path.exists("jsons"):
    os.makedirs("jsons")

print("Writing thesis '"+ jsondic["titles"][0]["title"] +"' metadata to file jsons/"+ out_filename+".json")
         
with io.open("jsons/"+ out_filename+".json", 'w', encoding='utf-8') as f: 
    f.write(unicode(json.dumps(jsondic, ensure_ascii=False, indent=4)))

#should be valid!
#try to validate with http://jeremydorn.com/json-editor/ and see the error messages!




#What about rights? Eg BASE may contain a rights field with description "Metadata may be used without restrictions as long as the oai identifier remains attached to it. "

