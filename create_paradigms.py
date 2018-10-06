#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 15:23:17 2018

@author: lena
"""
import re

def make_paradigms(entry_dict, templates):
    """ Make a dictionary, with key = lemma, values = a list per template that looks like:
        [lexeme, template_name, features, POS, [prefix, suffix, infixes], stem]"""

    paradigms = {}

    for word in entry_dict:
        paradigms[word] = []
        for word_lang in entry_dict[word]:
            for template in templates:
                if template == word_lang[0]:
                    try:
                        inflections = make_inflections(word, word_lang, templates[template], word_lang[-1])
                    except KeyError:
                        inflections = make_inflections(word, word_lang, templates[template], '')
                    if inflections != []:
                        paradigms[word].append(inflections)

        if paradigms[word] == [] or paradigms[word] == [[]]:
            del paradigms[word]

    return paradigms


def make_inflections(word, word_lang, template, finnish_a):
    """ Create the inflecions for all words.
        (finnish_a is an argument only required for fi-conj-... templates. """

    def find_affixes(wordtype):
        """ Function to fetch prefixes, suffixes and infixes from template. """
        prefix = ''
        suffix = ''
        infix = ''

        if re.search("([\w\s]+){{{", wordtype) is not None: #prefix
            prefix = re.search("([\w\s]+){{{", wordtype).group(1)
        if re.search("}}}([\w\s]+)", wordtype) is not None: #suffix
            suffix = re.search("}}}([\w\s]+)", wordtype).group(1)
        if re.search("}}}[\w\s]+{{{", wordtype) is not None: #infix(es)
            infix = re.findall("}}}([\w\s]+){{{", wordtype)

        return [prefix, suffix, infix]

    def find_pos(string):
        """ Find the POS of the wordtype, based on the template name. """
        pos = ''
        if 'adj' in string:
            pos = 'ADJ'
        elif 'verb' in string:
            pos = 'VERB'
        elif 'conj' in string:
            pos = 'VERB'
        elif 'noun' in string:
            pos = 'NOUN'
        elif 'decl' in string and not 'adj' in string:
            pos = 'NOUN'

        return pos

    def make_inflection_wordtypes(num, word_lang, new_word):
        """ It iterates over a new word, processes it, finds affixes in wordtype. """

        for n in range(num, len(word_lang)):
            new_word = new_word.replace("{{{" + str(n) + "}}}", word_lang[n])
        new_word = re.sub("\d", "", new_word)
        new_word = re.sub("[^\w\s]+", "", new_word)
        new_word = new_word.replace("xa0", '').strip()
        affixes = find_affixes(wordtype[0])
        if affixes[0] == '' and affixes[1] == '':
            stem = new_word
        else:
            stem = new_word[len(affixes[0]):-len(affixes[1])]

        return new_word, affixes, stem


    inflections = []

    schemata_with_stem = ['la-', 'de-conj', 'ang-conj-', 'nl-conj', 'ast-conj', 'as-',
                      'roa-', 'ga-decl', 'mt-prep-inflection-2', 'be-', 'nap-', 'sh-',
                      'gmq-', 'se-', 'grc-', 'ovd-', 'sk-decl-adj-', 'fi-decl', 'ar-',
                      'gu-', 'osx-decl-noun', 'osx-conj-', 'sms-', 'fo-', 'wbp-', 'is-',
                      'non-', 'mdf-', 'pl-', 'ku-', 'ka-', 'sq-', 'got-', 'et-', 'sl-',
                      'syc-', 'sc-', 'cu-', 'fa-', 'gl-', 'chm-', 'hi-', 'ku-', 'dsb-',
                      'lv-', 'ro-', 'lt-', 'hu-decl', 'egl-', 'frm-', 'gmh-', 'sga-', 
                      'ofs-', 'nds-', 'prg-', 'bn-', 'pt-', 'ur-', 'pjt-', 'ps-', 'psu-', 
                      'mk-', 'cel-', 'wbp-', 'sv-', 'myv-', 'scn-', 'tl-', 'tt-', 'xcl-',
                      'ae-', 'odt-', 'stq-', 'hit-', 'tn-', 'arz-', 'tr-', 'ca-', 'cy-', 
                      'sma-', 'ie-']

    # for schemata where the stem is not the same as the lemma
    if any(word_lang[0].startswith(x) for x in schemata_with_stem):

        for wordtype in template:
            new_word =  wordtype[0]
            new_word, affixes, stem = make_inflection_wordtypes(1, word_lang, new_word)

            inflections.append([new_word, word_lang[0], wordtype[1:], \
                                find_pos(word_lang[0]), affixes, stem])
        
    # for languages where the pattern doesn't include any stem (v. weird)
    elif word_lang[0] == 'hu-conj-gyek':

        for wordtype in template:

            new_word = word_lang[1] + wordtype[0]
            new_word, affixes, stem = make_inflection_wordtypes(2, word_lang, new_word)

            inflections.append([new_word, word_lang[0], wordtype[1:], \
                                find_pos(word_lang[0]), affixes, stem])

    # for languages where the pattern doesn't include any stem (v. weird)
    elif any(word_lang[0].startswith(x) for x in ['hu-conj', 'crh-latin-noun', 
                                                  'az-latin-', 'tr-infl']):

        for wordtype in template:

            new_word = word_lang[1] + wordtype[0]
            new_word, affixes, stem = make_inflection_wordtypes(2, word_lang, new_word)

            inflections.append([new_word, word_lang[0], wordtype[1:], \
                                find_pos(word_lang[0]), affixes, stem])

    # for spanish patterns who don't have the main stem
    elif any(word_lang[0].startswith(x) for x in ['es-conj']):
        for wordtype in template:       
            new_word = re.sub('\{\{\{\d\}\}\}', word[:-2], wordtype[0])
            new_word, affixes, stem = make_inflection_wordtypes(1, word_lang, new_word)

            inflections.append([new_word, word_lang[0], wordtype[1:], \
                                find_pos(word_lang[0]), affixes, stem])

    # finnish verbs change their a to ä, if the last argument is ä
    elif any(word_lang[0].startswith(x) for x in ['fi-conj']):
        for wordtype in template:
            new_word =  wordtype[0] # fetch stem
            new_word, affixes, stem = make_inflection_wordtypes(1, word_lang, new_word)
            if finnish_a == 'ä':
                new_word = new_word.replace("a", "ä").replace("ovät", "ovat") 

            inflections.append([new_word, word_lang[0], wordtype[1:], \
                                find_pos(word_lang[0]), affixes, stem])

    # for every other language
    else:

        for wordtype in template:
            new_word =  wordtype[0]
            new_word = new_word.replace("{{{1}}}", word)
            new_word, affixes, stem = make_inflection_wordtypes(2, word_lang, new_word)

            inflections.append([new_word, word_lang[0], wordtype[1:], \
                                find_pos(word_lang[0]), affixes, stem])

    return inflections
