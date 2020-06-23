# Wikinflection 

_Find the extracted, ready-to-use corpus at_ [github.com/lenakmeth/Wikinflection-Corpus](https://github.com/lenakmeth/Wikinflection-Corpus).

Massive semi-supervised generation of multilingual inflectional corpus from Wiktionary. Corresponding publication:
Metheniti, E., & Neumann, G. (2018, December). [Wikinflection: Massive Semi-Supervised Generation of Multilingual Inflectional Corpus from Wiktionary.](http://www.ep.liu.se/ecp/article.asp?issue=155&article=014&volume=) In Proceedings of the 17th International Workshop on Treebanks and Linguistic Theories (TLT 2018), December 13–14, 2018, Oslo University, Norway (No. 155, pp. 147-161). Linköping University Electronic Press.

## Getting Started

* Download the [XML wiki dump](https://dumps.wikimedia.org/enwiktionary/latest/enwiktionary-latest-pages-articles-multistream.xml.bz2) for the Englsih version of Wiktionary.
* Clone the project.

### Prerequisites

* Python3
* BeautifulSoup
* Pandas

### Run

From command line: `python main.py [dump file]`

### Notes

* The first time running, module `pull_templates.py` will pull 7K text files from [en.wiktionary.org](https://en.wiktionary.org/wiki). This process will take several hours, because of pauses between requests, and will use up ~210MB. 
* The output will be a .JSON file with inflectional paradigms, evaluated and corrected, separated per lemma, then separated by template ID. Every word in the inflectional paradigm has: template ID, [list of morphological features], POS, [prefixes, suffixes, [infixes]], stem.
* Currently, there are problems with the HTML table parsing (merged cells, nested tables in tables), and as a result not all features are identified per wordform. This is a known issue and is under work.

## Authors

* **Eleni Metheniti** - *Initial work* - [lenakmeth](https://github.com/lenakmeth)
