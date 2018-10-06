#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run this file as:
python main.py --xml file 

@author: lenakmeth
"""

import os, io, json, sys
from make_corpus import open_dump
from pull_templates import find_templates, template_download
from read_templates import open_templates
from create_paradigms import make_paradigms
from evaluation import make_per_template, evaluate_templates, correct_templates

if __name__ == "__main__":
    
#    dump_file = sys.argv[1]
    dump_file = "/Users/lena/Desktop/enwiktionary-20180801-pages-articles-multistream.xml"
    
    # make the languages list, the entries dictionary, fetch template names
    languages, entry_dict, templates_names = open_dump(dump_file)
    
    # find how many templates have been downloaded or not
    templates_folder = os.getcwd() + "/Templates"
    
    # open UD tags list
    tags_filename = os.getcwd() + "/ud_tags.csv"
    
    # download the templates if they don't exist
    if not os.path.isdir(templates_folder):
        os.mkdir("Templates")
    to_download = find_templates(templates_folder, templates_names)
    
    if len(to_download) > 0:
        print("Downloading " + str(len(to_download)) + " files...\n")
        template_download(to_download, templates_folder)
        
    # open the template files and read them in a tempaltes dictionary
    templates = open_templates(templates_folder, tags_filename)

    # create paradigm for every dictionary entry
    paradigms = make_paradigms(entry_dict, templates)
    
    # evaluation -- find incorrect templates
    dict_per_template = make_per_template(paradigms)
    evaluated_templates = evaluate_templates(dict_per_template)
    
    # return corrected templates and re-run the paradigms 
    corrected_templates = correct_templates(templates)
    corrected_paradigms = make_paradigms(entry_dict, corrected_templates)
    
    # make JSON file of lemmata, per language, per POS
    with io.open("lemmata.json", "w", encoding="utf-8") as f:
        json.dump(corrected_paradigms, f)
       
