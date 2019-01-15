#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The module to open the XML wiki dump, English. If used with other target 
language, please update function edit_entry with correct headings.

@author: lenakmeth
"""

import re

def open_dump(filename):
    """ Main function, opens the wikidump and saves the word dictionary, 
        the templates and the modules. """
        
    with open(filename, 'r', encoding="utf-8") as f:
        temp = ''
        languages = {}
        dictionary = {}
        templates_names = []
        marker = True

        for line in f:
            if "</page>" in line:
                marker = False
            else:
                marker= True
            
            if marker:
                temp += line.replace("&amp;", " ").replace("<\text>", '').replace("\xa0", '')
            else:
                # find the title of the page
                if re.search("<title>(.+)</title>", temp) is not None:
                    title = re.search("<title>(.+)</title>", temp).group(1)
                
                # remove notes that mess up inflection-conjugation
                if re.search("note=.+}}", temp) is not None:
                    temp = re.sub("note=.+}}", '', temp)
    
                # find the pages with the language codes
                if "Module:languages/data" in title:
                    languages = {**languages, **edit_languages(temp)}           
    
                # find template pages names (to download)
                elif title.startswith("Template:"):
                    if not any(x in title for x in ["documentation", "table"]):
                        if any(x in title for x in ["noun", "adj", "verb", "decl", "conj", "infl", "decl"]):
                            templates_names.append(title)

                # find all inflection/conjugation paradigms from word pages
                elif not ":" in title:
                    if "=Inflection=" or "=Conjugation=" or "=Declension=" in temp:
                        values = edit_entry(temp)
                        
                        if values != [] and values != [[]]:
                            dictionary[title] = values
                                    
                temp = ''
                                      
    return languages, dictionary, templates_names


def edit_languages(string):
    """ The languages come from data modules. This function only pulls the id
        and the name of the language, there is more info in the modules. All
        modules here: en.wiktionary.org/wiki/Category:Language_data_modules"""
        
    l = {}
    string = string.replace("&quot;", '"')
    
    for i in string.split("\n\nm"):
        if re.search('\["[\w-]+"\]', i) is not None:
            lang_id = re.search('\["([\w-]+)"\]', i).group(1)
        if re.search('\{\\n\\t"([\w\(\)\s\'\!-]+[^\d])",[^\}\]]', i) is not None:
            lang_name = re.search('\{\\n\\t"([\w\(\)\s\'\!-]+[^\d])",[^\}\]]', i).group(1)
            l[lang_id] = lang_name
        
    return l


def edit_entry(string):
    """ Edit pages that have a lemma which has inflection. """
    
    # The three different loops exist because entries have multiple languages, 
    # and all need to be captured.
    
    values = []
    
    if "=Inflection=" in string:
        for x in re.findall("Inflection={4,7}\s?\\n{{([\[\]\w\s\|\|\-=\-.]+)}}\s?[<\/text>]?\\n?", string):
            temp = []
            for i in x.strip().split("|"):
                if not any(y in i for y in ['rfinfl', '=']):
                    temp.append(i.strip())
            values.append(temp)
      
    if "=Conjugation=" in string:
        for x in re.findall("Conjugation={4,7}\s?\\n{{([\[\]\w\s\|\|\-=\-.]+)}}\s?[<\/text>]?\\n?", string):
            temp = []
            for i in x.strip().split("|"):
                if not any(y in i for y in ['rfinfl', '=']):
                    temp.append(i.strip())
            values.append(temp)
            
    if "=Declension=" in string:
        for x in re.findall("Declension={4,7}\s?\\n{{([\[\]\w\s\|\|\-=\-.]+)}}\s?[<\/text>]?\\n?", string):
            temp = []
            for i in x.strip().split("|"):
                if not any(y in i for y in ['rfinfl', '=']):
                    temp.append(i.strip())
            values.append(temp)
    
    return values
