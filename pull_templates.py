#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NB= Reduce time in line 28 if necessary, but no less than 1s between requests.

@author: lenakmeth
"""

import os
import requests
import random
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def template_download(templates, directory):
    """ Downloads templats from the english wiktionary. 
        If using differnet language, update urls. 
        If IP address blocked, use higher values in pause_between_request. """
    
    urls = ["https://en.wiktionary.org/wiki/" + t for t in templates]    
    
    for u in urls:
        
        title = u[40:]

        pause_between_request = random.randint(5,10)
        time.sleep(pause_between_request)
        
        print('Downloading ' + title + "...")
        
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        r = session.get(u)
        
        print('Request successful!')
        
        with open(directory + '/' + title.replace("/", "&") + ".txt", 'w', encoding='utf-8') as f:
            f.write(r.text)
            print('Saved as ' + title.replace("/", "&") + ".txt")
            print()


def find_templates(templates_folder, templates_names):
    """ Finds which templates need to be downloaded, in case there are none
        downloaded or there are new ones online. """
        
    templates = []
    
    downloaded = [i[:-4] for i in os.listdir(templates_folder) if i.endswith(".txt")]
    
    for t in templates_names:
        if t[9:] not in downloaded:
            templates.append(t)

    
    return templates