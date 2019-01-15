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
from collections import Counter


def read_tags(filename):
    """ Open the file with the ud tags."""
    
    tags = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            tags[line.split(',')[0]] = [i for i in line.strip().split(',')[1:] if i != '']
        
    return tags


def replace_tags(arg, ud_tags):
    """ Replace tags in template file with UD tags. """
    
    new_tag = []
    tags = arg.lower().replace("\\", " ").replace('/', '').replace('\xa0', ' ').split(" ")
    for tag in tags:
        if 0 < len(tag) < 500:
            for t in ud_tags:
                for i in ud_tags[t]:
                    if i == tag:
                        new_tag.append(t)
    
    return new_tag


def fix_tags(entry):
    """ The table reading function is overzealous, e.g. it will find all tags 
        above/left of the cell, "singular" and "plural". We need to keep only 
        the last tag (lowest or right-est). This problem occurs because of 
        nested tables used by most Wiki templates. """
        
    new_entry = [entry[0]]
    
    temp = {}
    for tag in entry[1:]:
        if '=' in tag:
            temp[tag.split('=')[0]] = tag.split('=')[1]
    
    for tag in temp:
        if tag + '=' + temp[tag] not in new_entry:
            new_entry.append(tag + '=' + temp[tag])

    return new_entry


def my_read_html(filename):
    """ Open a template file (as downloaded in the files) and find the table
        with the inflections. """
    
    # find all tables from html
    with open(filename, 'r', encoding='utf-8') as f:
        marker = False
        fi_decl= False
        tables = []  
        t = ''
        rowspan = ''
        rowspan_start = False
        line_counter = 0
        
        for line in f:
            
            line_counter += 1
            
            # marker to mark fi-decl templates, which are problematic
            if "fi-decl" in line:
                fi_decl = True
                
            # find table start
            if "<table" in line:
                marker = True
                
            # find table end
            elif "/table" in line:
                marker = False
                
            # save table to process it
            if marker:
                
                #unmerge cells directly in the HTML code. Pandas does not read
                #merged cells, and even with function read_html_table makes mistakes.
                #This code will find "colspan=X" in HTML line and multiply the cell 
                #X times. 
                
                # force empty cell
                if 'rowspan=' in line:
                    if BeautifulSoup(line.replace('&quot;', ''), "lxml").text == '\n':
                        line = line.strip() + 'EMPTY\n'
                    
                if 'colspan=' in line:
                    content = BeautifulSoup(line.replace('&quot;', ''), "lxml").text
                    if content == '':
                        content = 'EMPTY' # force empty cell that's not NaN
                    num = int(re.search('colspan="(\d+)\W?"', line.replace('&quot;', '')).group(1))
                    
                    if content and num:
                        line = '<th>' + content + ('</th> <th>' + content) * (num-1)
                 
                
#                    num = int(re.search('rowspan="(\d+)\W?"', line.replace('&quot;', '')).group(1))
#                    rowspan_start = line_counter
#                    
#                    if content and num:
#                        rowspan = ' ' + re.sub('</?th>', '', content.strip())
#                        
#                elif rowspan_start:
#                    if rowspan_start -1 < line_counter < rowspan_start + num*2:
##                        print(line)
#                        line = rowspan + line
##                        print(line)
#                    
#                else:
#                    rowspan = ''
#                    rowspan_start = False
                
                t += line
                
            
            # table is over, time to process it            
            else:
                
                t = re.sub("<sup>\w+</sup>", '', t) # get rid of notes
                t = re.sub("\(.+\)", '', t) # get rid of parentheses
                t = t.replace('<p>', '<td>').replace('</p>', '</td>')
                t = t.replace('<br />', '/').replace('\\xa0', ' ').replace('\xa0', ' ')#.replace('\\n', ' ')
                if re.search("\{\{\{\d\}\}\}", t) is not None:     
                    
                    try:
                        table = read_html_table(t)
                        if fi_decl: # fi-decl templates are read incorrectly
                            table = table.loc[:,[0,1,2]]
                    except IndexError:
                        table = pd.read_html(t)[0]
                        if fi_decl:
                            table = table.loc[:,[0,1,2]]
                    except ValueError:
                        table = pd.read_html(t)[0]
                        if fi_decl:
                            table = table.loc[:,[0,1,2]]
                    except AttributeError:
                        table = pd.read_html(t)[0]
                        if fi_decl:
                            table = table.loc[:,[0,1,2]]
                        
                    tables.append(table)
                    
                t = ''
                  
    return tables


def read_html_table(html_string):
    """ Code adapted by J. Ricco: https://johnricco.github.io/2017/04/04/python-html/ 
        This code will unmerge ALL cells in a table, not just 1st column/row. """
    
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

    
    # For every column, copy contents from top unmerged cell to bottom unmerged cell
    for column in range(n_cols):
        for num in range(n_rows):
            if type(df.loc[num, column]) != str:
                if num > -1 and type(df.loc[num-1, column]) == str:
                    df.loc[num, column] = df.loc[num-1, column]
                
#                
#    # For every row, copy contents from left unmerged cell to right unmerged cell
#
#    for row in reversed(range(n_rows)):
#        for num in reversed(range(n_cols)):
##            print(row, num)
#            if type(df.loc[row, num]) != str:
#                print(df.loc[row, num])
#                print(df.loc[row, num-1])
#                try:
#                    print(df.loc[row, num-1])
#                    df.loc[row, num] = df.loc[row, num+1]
#                except KeyError:
#                    df.loc[row, num] = df.loc[row, num]
                    
    return df


def find_wordforms(df, ud_tags):
    """ Reads the dataframe and will return a list of the wordforms of the template. """
    
    
    def make_entry(word, row, col, df, ud_tags):
        """ Look into a cell and create the word entry. """
        
        entry = []
        
        for i in ['(', ')', ']', '[', '/']: #remove garbage
            word = word.replace(i, '')
        word = re.sub('#.+', '', word) #remove comments
        word = word.replace('num=sg', '{{{1}}}') #stem = singular allomorph
        word = word.replace('crh-latin-noun', '') #special for template
        
        entry.append(word)
        
#        # find all features in the cell's column, with threshold of 16 cells to top
#        for r in range(row-16, row):
#            if r > -1: 
#                if type(df.iloc[r, col]) == str and not "{{{" in df.iloc[r, col]:
#                    entry.append(df.iloc[r, col])
#                    entry += replace_tags(df.iloc[r, col], ud_tags)
#        
#        # find all features in the cell's row, with threshold of 10 cells to the left
#        for c in range(col-10, col):
#            if c > -1:
#                if type(df.iloc[row, c]) == str and not "{{{" in df.iloc[row, c]:
##                    entry.append(df.iloc[row, c])
#                    entry += replace_tags(df.iloc[row, c], ud_tags)
        
        # find all features in the cell's column
        for r in range(row):
            if type(df.iloc[r, col]) == str and not "{{{" in df.iloc[r, col]:
                entry += replace_tags(df.iloc[r, col], ud_tags)
        
        # find all features in the cell's row
        for c in range(col):
           if type(df.iloc[row, c]) == str and not "{{{" in df.iloc[row, c]:
               entry += replace_tags(df.iloc[row, c], ud_tags)

        return fix_tags(entry)
    
    
    wordforms = []
    
    for row in range(len(df.iloc[:, 0])):
        
        for col in range(len(df.iloc[row,:])):
            if type(df.iloc[row,col]) == str and "{{{" in df.iloc[row,col]:
                
                # cells with a second wordform in ()
                if "(" in df.iloc[row,col]:
                    if len(df.iloc[row,col]) < 500:
                        for w in df.iloc[row,col].split("("):
                            if "{{{" in w:
                                wordforms.append(make_entry(w, row, col, df, ud_tags))
                
                # cells with a second wordform split by comma
                elif ", " in df.iloc[row,col] and not " -" in df.iloc[row,col]:
                    if len(df.iloc[row,col]) < 500:
                        for w in df.iloc[row,col].split(", "):
                            if "{{{" in w:
                                wordforms.append(make_entry(w, row, col, df, ud_tags))
                            
                # cells with a second wordform split by /
                elif "/" in df.iloc[row,col] and not " -" in df.iloc[row,col]:
                    if len(df.iloc[row,col]) < 500:
                        for w in df.iloc[row,col].split("/"):
                            if "{{{" in w:
                                wordforms.append(make_entry(w, row, col, df, ud_tags))
                
                # cells with a second wordform split by =
                elif " = " in df.iloc[row,col] and not " -" in df.iloc[row,col]:
                    if len(df.iloc[row,col]) < 500:
                        for w in df.iloc[row,col].split(" = "):
                            if "{{{" in w:
                                wordforms.append(make_entry(w, row, col, df, ud_tags))
                
                # cells with a second wordform, only suffix is written 
                elif ", -" in df.iloc[row,col]:
                    if len(df.iloc[row,col]) < 500:
                        if "{{{" in df.iloc[row,col]:
                            w1 = df.iloc[row,col].split(', -')[0]
                            wordforms.append(make_entry(w1, row, col, df, ud_tags))
                            w2 = re.sub(r'(.*\{\{\{\d\}\}\})\w+', r'\1', w1) + df.iloc[row,col].split(' -')[1]
                            wordforms.append(make_entry(w2, row, col, df, ud_tags))
                                                    
                # normal cells with only one wordform
                else:
                    if len(df.iloc[row,col]) < 500:
                        wordforms.append(make_entry(df.iloc[row,col], row, col, df, ud_tags))
      
    return wordforms


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
        templates[i] = find_wordforms(tables[i][0], ud_tags)
       
    return tables, templates  
    