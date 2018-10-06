#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 23:21:49 2018

@author: lena
"""

import pandas as pd
import os
import re
from bs4 import BeautifulSoup 
import copy


def read_tags(filename):
    """ Open the file with the ud tags."""
    
    tags = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            tags[line.split(',')[0]] = line.strip().split(',')[1:]
        
    return tags


def replace_tags(arg, ud_tags):
    """ Replace tags in template file with UD tags. """
    
    new_tag = []
    tags = arg.lower().replace("\\", " ").split(" ")
    for tag in tags:
        for t in ud_tags:
            for i in ud_tags[t]:
                if i == tag:
                    new_tag.append(t)
    
    return new_tag


def my_read_html(filename):
    """ Open a template file (as downloaded in the files) and find the table
        with the inflections. """
    
    # find all tables from html
    with open(filename, 'r', encoding='utf-8') as f:
        marker = False
        tables = []  
        t = ''
        for line in f:
            if "<table" in line:
                marker = True
            elif "/table" in line:
                marker = False
            if marker:
                t += line
            else:
                t = re.sub("<sup>\w+</sup>", '', t) # get rid of notes
                t = re.sub("\(.+\)", '', t) # get rid of parentheses
                t = t.replace('<p>', '<td>').replace('</p>', '</td>')
                t = t.replace('<br />', '/').replace('\\n', ' ').replace('\\xa0', ' ').replace('\xa0', ' ')
                if re.search("\{\{\{\d\}\}\}", t) is not None:     
                    
                    try:
                        tables.append(read_html_table(t))
                    except IndexError:
                        tables.append(pd.read_html(t)[0])
                    except ValueError:
                        tables.append(pd.read_html(t)[0])
                    except AttributeError:
                        tables.append(pd.read_html(t)[0])
                t = ''
                  
    return tables


def read_html_table(html_string):
    """ Code adapted by John Ricco.
        https://johnricco.github.io/2017/04/04/python-html/ """
    
    soup = BeautifulSoup(html_string, 'lxml') # Parse the HTML as a string
    tables_html = soup.find_all('table')[0] # Grab the first table

    n_cols = 0
    n_rows = 0
    
    for row in tables_html.find_all("tr"):
        col_tags = row.find_all(["td", "th"])
        if len(col_tags) > 0:
            n_rows += 1
            if len(col_tags) > n_cols:
                n_cols = len(col_tags)
    
    # Create dataframe
    df = pd.DataFrame(index = range(0, n_rows), columns = range(0, n_cols))
    
    	# Create list to store rowspan values 
    skip_index = [0 for i in range(0, n_cols)]
			
    # Start by iterating over each row in this table...
    row_counter = 0
    for row in tables_html.find_all("tr"):
        # Skip row if it's blank
        if len(row.find_all(["td", "th"])) == 0:
            next
        else:
            # Get all cells containing data in this row
            columns = row.find_all(["td", "th"])
            col_dim = []
            row_dim = []
            col_dim_counter = -1
            row_dim_counter = -1
            col_counter = -1
            this_skip_index = copy.deepcopy(skip_index)
            
            for col in columns:
                
                # Determine cell dimensions
                colspan = col.get("colspan")
                if colspan is None:
                    col_dim.append(1)
                else:
                    col_dim.append(int(colspan))
                col_dim_counter += 1
                    
                rowspan = col.get("rowspan")
                if rowspan is None:
                    row_dim.append(1)
                else:
                    row_dim.append(int(rowspan))
                row_dim_counter += 1
                    
                # Adjust column counter
                if col_counter == -1:
                    col_counter = 0  
                else:
                    col_counter = col_counter + col_dim[col_dim_counter - 1]
                    
                while skip_index[col_counter] > 0:
                    col_counter += 1

                # Get cell contents  
                cell_data = col.get_text()
                
                # Insert data into cell
                df.iat[row_counter, col_counter] = cell_data.strip()

                # Record column skipping index
                if row_dim[row_dim_counter] > 1:
                    this_skip_index[col_counter] = row_dim[row_dim_counter]
        
        # Adjust row counter 
        row_counter += 1
        
        # Adjust column skipping index
        skip_index = [i - 1 if i > 0 else i for i in this_skip_index]
    
    # For first row, copy contents from first unmerged cell to the other unmerged cells
    for num in range(len(df.loc[0,:])):
        if type(df.loc[0][num]) != str:
            df.loc[0][num] = df.loc[0][num-1]
            
    # For first column, copy contents from first unmerged cell to the other unmerged cells
    for num in range(len(df.loc[:, 0])):
        if type(df.loc[num, 0]) != str:
            df.loc[num, 0] = df.loc[num-1, 0]
    
    return df


def find_lexemes(df, ud_tags):
    """ Reads the dataframe and will return a list of the lexemes of the template. """
    
    lexemes = []
    
    def make_entry(word, temp, df, col, header_row, second_header_row, ud_tags):
        """ Iterate per line. """
        
        entries = []
        
        for i in ['(', ')', '/', ']', '[']: #remove garbage
            word = word.replace(i, '')
        word = re.sub('#.+', '', word) #remove comments
        word = word.replace('num=sg', '{{{1}}}') #stem = singular allomorph
        word = word.replace('crh-latin-noun', '') #special for template
        
        entries.append(word)
        
        if type(temp[0]) == str:
            feat_1 = temp[0].replace('\xa0', ' ')
            for f in feat_1.split(' '):
                if not "{{{" in f and len(f)<25:
                    entries += replace_tags(f, ud_tags)
            
        if header_row > -1:
            if type(df[0][col][header_row]) == str:
                feat_2 = df[0][col][header_row].replace('\xa0', ' ')
                for f in feat_2.split(' '):
                    if not "{{{" in f and len(f)<25:
                        entries += replace_tags(f, ud_tags)
            
        if second_header_row > -1:
            if type(df[0][col][second_header_row]) == str:
                feat_3 = df[0][col][second_header_row].replace('\xa0', ' ')
                for f in feat_3.split(' '):
                    if type(f) == str and not "{{{" in f and len(f)<25:
                        entries += replace_tags(f, ud_tags)

        return entries
    
    
    # find header row 
    header_row = -1 # if no header row is found
    second_header_row = -1
    # possible tags which denote that the line is a header - update if necessary
    tags = ["weak", "sing.", "masculine", "masc.", "singular", 'participle'
            "person", "present", "first", "male", "subjunctive", '1st', 
            "nominative", "1st person", 'auxiliary', 'passive', 'definite',]
    for num in range(len(df[0].loc[:,0])):
        temp = list(df[0].loc[num])
        if any(tag in x.lower() for tag in tags for x in temp if type(x) == str):
            header_row = num
        elif any(tag in x.lower() for tag in tags for x in temp if type(x) == str):
            second_header_row = num
        elif any(tag in x.lower() for tag in tags for x in temp if type(x) == str):
            second_header_row = num
    
    # iterate per line
    for num in range(len(df[0].loc[:,0])):
        temp = list(df[0].loc[num])
        for i in temp:
            if type(i) == str and re.search('{{{\d+}}}', i) is not None:
                col = temp.index(i)
                for word in i.split("/"):
                    if "(" in word:
                        for w in word.split("("):
                            if "{{{" in w:
                                lexemes.append(make_entry(w, temp, df, col, header_row, second_header_row, ud_tags))
                    elif ", " in word and not " -" in word:
                        for w in word.split(", "):
                            if "{{{" in w:
                                lexemes.append(make_entry(w, temp, df, col, header_row, second_header_row, ud_tags))
                    elif ", -" in word:
                        if "{{{" in word:
                            w1 = word.split(', -')[0]
                            lexemes.append(make_entry(w1, temp, df, col, header_row, second_header_row, ud_tags))
                            w2 = re.sub(r'(.*\{\{\{\d\}\}\})\w+', r'\1', w1) + word.split(' -')[1]
                            lexemes.append(make_entry(w2, temp, df, col, header_row, second_header_row, ud_tags))                            
                    else:
                        if "{{{" in word:
                            lexemes.append(make_entry(word, temp, df, col, header_row, second_header_row, ud_tags))
                    
    return lexemes


def open_templates(directory, tags_filename):
    """ Opens templates from folder. """
    
    files = [file for file in os.listdir(directory) if file.endswith(".txt")]
    ud_tags = read_tags(tags_filename)
    
    tables = {}
    for file in files:
         page = my_read_html(directory + '/' + file)
         if page != []:
            tables[file[:-4].replace("&","/")] = page
        
    templates = {}
    for i in tables:
        templates[i] = find_lexemes(tables[i], ud_tags)
       
    return templates  
    