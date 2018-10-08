# Wikinflection 

Massive semi-supervised generation of multilingual inflectional corpus from Wiktionary.

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

## Authors

* **Eleni Metheniti** - *Initial work* - [lenakmeth](https://github.com/lenakmeth)