# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template.loader import get_template
from django.shortcuts import render
from django.http import HttpResponse
from .models import Publisher, Author, Book

import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import lxml.html
import re
import sys
import csv
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup

#options
ACM_BASE_URL = 'https://dl.acm.org/'
ACM_SEARCH_URL = ACM_BASE_URL + "results.cfm?within=owners.owner%3DGUIDE&srt=_score&query=persons.authors.personName:"

Gscholar_URL = 'https://scholar.google.com.eg/citations?view_op=search_authors&hl=en&mauthors=label:'

DBLP_BASE_URL = 'http://dblp.uni-trier.de/'
DBLP_SEARCH_URL = DBLP_BASE_URL + "search?q="


driver = webdriver.Chrome() # wen need to check Phantom js which is hidden and may be faster...
driverAcm = webdriver.Chrome() # wen need to check Phantom js which is hidden and may be faster...

def query_DBLP(authorName):

    driver = webdriver.Chrome()
    driver.get(DBLP_SEARCH_URL+""+authorName)
    html = driver.page_source
    time.sleep(1)
    elem = driver.find_element_by_tag_name("body")
    no_of_pagedowns = 50
    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.1)
        no_of_pagedowns-=1
    html = driver.page_source
    soup = BeautifulSoup(html,"lxml")
    
    authorsSoup=soup.findAll('span', attrs={"itemprop": "author"})
  
    co_auths=[]
    for author in authorsSoup:
        co_auths.append(author.text)

    co_auths= (list(set(co_auths)))
    return co_auths

def query_Acm(authorName):
    
    driverAcm.get(ACM_SEARCH_URL+""+authorName)
    affHist=[]
    try:
        linkAcmPAuthors= driverAcm.find_element_by_link_text(authorName)
        linkAcmPAuthors.click()
        affHistElems=driverAcm.find_elements_by_xpath("/html/body/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/div/a")
        
        for aff in affHistElems:
            affHist.append(aff.text)
    except:
        print ('Link to be clicked cannot be found!')        

    return affHist    

def getURL(Prev_Next_url):
    url=Prev_Next_url
    url=url.replace("\\x3d","=")
    url=url.replace("\\x26","&")
    url=url.replace("&oe=ASCII","")
    url=url.replace("window.location='","https://scholar.google.com.eg")
    url=url.replace("'","")
    return url

def scrapeAuthorInfo():
    authors=driver.find_elements_by_xpath('//*[@class="gsc_1usr gs_scl"]')
    
    nameslst=[]
    emailslst=[]
    citationslst=[]
    linkslst=[]
    topicslst=[]
    Affliationslst=[]
    imageslst=[]

    
    for author in authors:
        
        
        name= author.find_element_by_xpath('.//h3[@class="gsc_oai_name"]/a').get_attribute('innerHTML')
        
        link= author.find_element_by_xpath('.//h3[@class="gsc_oai_name"]/a').get_attribute('href') 
        
        image=author.find_element_by_xpath('.//span[@class="gs_rimg gsc_pp_sm gsc_1usr_photo"]/img').get_attribute('src')
        
        Afflst=[] 
        Affliation=author.find_element_by_xpath('.//*[@class="gsc_oai_aff"]').get_attribute('innerHTML')
        Afflst.append(Affliation)
        
        email=author.find_element_by_xpath('.//*[@class="gsc_oai_eml"]').get_attribute('innerHTML')
        email=str(email).replace('Verified email at ', '')
        
        citedby=author.find_element_by_xpath('.//*[@class="gsc_oai_cby"]').get_attribute('innerHTML')
        citedby=str(citedby).replace('Cited by ', '')

        topicslist=[]
        topics=author.find_elements_by_xpath('.//*[@class="gsc_oai_one_int"]')
        for topic in topics:
            topicslist.append(topic.text)

        affHist=query_Acm(name)
        Afflst.append(affHist)

        '''driverAcm.get(ACM_SEARCH_URL+""+name)
        try:
            linkAcm = driverAcm.find_element_by_link_text(name)
            linkAcm.click()
            affHistElems=driverAcm.find_elements_by_xpath("/html/body/div[2]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/table/tbody/tr/td/div/a")
            affHist=[]
            for aff in affHistElems:
                affHist.append(aff.text)
            Afflst.append(affHist)
        except:
            print ('Link to be clicked cannot be found!')'''

        nameslst.append(name)
        Affliationslst.append(Afflst)
        emailslst.append(email)
        citationslst.append(citedby)
        linkslst.append(link)
        topicslst.append(topicslist)
        imageslst.append(image)

    authorsDict={'Name':nameslst,'Image':imageslst,'AffiliationHistory':Affliationslst,'Email':emailslst,'Link' :linkslst,'CitedBy':citationslst,'Topics':topicslst}
    return authorsDict        

def gscholarScrape(topics):
    
    topicslst=topics.split(',')
    completeAuthorsDataframe=[]

    for topic in topicslst:
        driver.get(Gscholar_URL+""+topic)    
        firstpageDict=scrapeAuthorInfo()
        firstAuthorsDataframe=pd.DataFrame.from_dict(firstpageDict,orient='index').transpose()

        completeAuthorsDataframe.append(firstAuthorsDataframe)

        Prev_Next_url=''
        Prev_Next=[]
        try:  
            Prev_Next =driver.find_element_by_xpath("//button[@type='button'][@aria-label='Next']").get_attribute('onclick')
            Prev_Next_url=str(Prev_Next)
            Prev_Next_url=getURL(Prev_Next_url)

        except Exception, e:
            pass
        else:
            pass
        finally:
            pass
        
        while (Prev_Next):
            driver.get(Prev_Next_url)    
            
            nextDict=scrapeAuthorInfo()
            nextAuthorsDataframe=pd.DataFrame.from_dict(nextDict,orient='index').transpose()
            completeAuthorsDataframe.append(nextAuthorsDataframe)
            
            try:  
                Prev_Next =driver.find_element_by_xpath("//button[@type='button'][@aria-label='Next']").get_attribute('onclick')
                Prev_Next_url=str(Prev_Next)
                Prev_Next_url=getURL(Prev_Next_url)
            except Exception, e:
                Prev_Next_url=''
            else:
                pass
            finally:
                pass

    resultedFullDF=pd.concat(completeAuthorsDataframe)

    return resultedFullDF

def search(request):
    error = False
    if 'q' in request.GET:
        q = request.GET['q']
        co_auths=[]
        if not q:
            error = True
        else:
            authors=q.split(',')
            affliationsList=[]
            for author in authors:
                affliations=query_Acm(author)
                affliationsList.append(affliations)
                coauthors=query_DBLP(author)
                co_auths.append(coauthors)

            return render(request, 'co_authors.html', {'co_auths': co_auths, 'Affiliations':affliationsList})

    return render(request, 'search_form.html', {'error': error})



	