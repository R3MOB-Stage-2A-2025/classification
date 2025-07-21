# parsing

A *python* module to parse a *json* file of a publication that is
written in the *Crossref style*.

# How to use

There are mainly two ways of using it:

1. When you have the full publication and you want to parse it.

```python
publication: str = json.dumps(full_json_publication)
publication_parsed = JsonParserCrossref(publication)

# If you want to get all the useful data to classify the publication.
metadata: dict[str, str | list[str]] = publication_parsed.line_json()
list(medatadata.keys()) == [
    "DOI",
    "OPENALEX",
    "title",
    "abstract",
    "topics",
    "given_keywords",
    "concepts",
    "sustainable_goals"
] # True

# If you want to get a text to classify.
# This is the concatenation of all the  metadata above.
text_to_classify: str = publication_parsed.classify_me()

# Example:
text_to_classify = "Decarbonisation of the shipping sector – Time to\
ban fossil fuels?, , Maritime Transport Emissions and Efficiency,\
Environmental Engineering, Environmental Science, Physical Sciences,\
Maritime Ports and Logistics, Industrial and Manufacturing Engineering,\
Engineering, Physical Sciences, Hybrid Renewable Energy Systems,\
Energy Engineering and Power Technology, Energy, Physical Sciences,\
Time line, Position (finance), Greenhouse gas, Fossil fuel, Timeline,\
Natural resource economics, Climate change, Position (finance),\
Business, Climate change mitigation, Economics, Finance, Engineering,\
Ecology, Geography, Archaeology, Biology, Waste management,\
Affordable and clean energy\
"
```

Here, only the title is not parsed,
and only the title and the abstract are not tokenized.

2. When you have only the dictionary from `JsonParserCrossref.line_json()`.

You will probably want to convert this dictionary into a text to classify,
which can be done using these commmands:

```python
# Don't have the full publication, but only metadata?
metadata: dict[str, str | list[str]] = {} # `JsonParserCrossref.line_json()`

# Try this!
text_to_classify: str = JsonParserCrossref().classify_me(line_json=metadata)
```

## Overview

This is the generic *json* format for a publication in this project.
You can see here all the keys of this *Crossref Style json*:

```json
[
  "DOI",
  "ISSN",
  "OPENALEX",
  "TL;DR",
  "URL",
  "abstract",
  "abstract_inverted_index",
  "author",
  "concepts",
  "container-title",
  "container-url",
  "keywords",
  "publication_date",
  "publisher",
  "reference",
  "related",
  "sustainable_development_goals",
  "title",
  "topics",
  "type"
]
```


The objects are sorted into "sub json files" to improve the parsing experience:

```python
# result of JsonParserCrossref.human_readable()
human_readable = {
    "title": self._title, # str
    "abstract": self._abstract, # str, this one might be missing (copyright).
                                # OpenAlex gives sometimes a generated version
                                # of the abstract ( `abstract_inverted_index` )
}

# result of JsonParserCrossref.ID()
ID = {
    "DOI": self._DOI, # str, regex used to find the DOIs: 
                      # `r'10\.\d{4,9}/[\w.\-;()/:]+'`
    "OPENALEX": self._OPENALEX, # str, example: 'https://openalex.org/Wxxxxx'
    "URL": self._URL, # str, example: 'https://doi.org/' + self._DOI
}

# result of JsonParserCrossref.publisher()
publisher = {
    "TYPE": self._TYPE, # str, example: "article", "book", "book-chapter".
                        # Types from Openalex , and if not found, Crossref.
    "ISSN": self._ISSN, # str
    "publisher": self._publisher, # str, example: "IEEE toto etc.."
    "container-title": self._container_title, # str, the corpus name.
    "container-url": self._container_url, # list[str]
    "publication_date": self._publication_date, # str
}

# result of JsonParserCrossref.people()
authors = self._authors # list[dict], directly retrieved from Openalex.

# Example:
authors = [
    {
      "given": "Leo",
      "family": "Mendiboure",
      "ORCID": "https://orcid.org/0000-0001-6643-9567",
      "OPENALEX": "https://openalex.org/A5088550595",
      "affiliation": [
        {
          "name": "Université Gustave Eiffel",
          "openalex": "https://openalex.org/I4210154111",
          "ror": "https://ror.org/03x42jk29",
          "country": "FR"
        },
        # ...
      ]
    },
    # ...
]

# result of JsonParserCrossref.similarities()
similarities = {
    "reference": self._reference, # list[dict], what the publication is citing.
    "related": self._related, # list[dict], what Openalex thinks
                              # the publication is related to.
}

# Example ( same format for "related" ):
reference = [
{
    "key": 1,
    "OPENALEX": "https://openalex.org/W55747394"
},
{
    "key": 2,
    "OPENALEX": "https://openalex.org/W4200024937"
},
# ...
]

# result of JsonParserCrossref.keywords()
keywords = {
    "topics": self._topics, # list[str] from Openalex
    "keywords": self._keywords, # list[str] from Openalex
    "concepts": self._concepts, # list[str] from Openalex
}

# result of JsonParserCrossref.miscellenaous()
miscellenaous = {
    "sustainable_development_goals":\
        self._sustainable_development_goals, # list[str] from Openalex
    "abstract_inverted_index":\
        self._abstract_inverted_index, # list[str] from Openalex
}

# Example ( same format as "keywords", "concepts",
#           "sustainable_development_goals" ):
topics = [
  "Bone Tissue Engineering Materials",
  "Biomedical Engineering",
  "Engineering",
  "Physical Sciences",
  "Calcium Carbonate Crystallization and Inhibition",
  "Biomaterials",
  "Materials Science",
  "Physical Sciences",
  "Dental Implant Techniques and Outcomes",
  "Oral Surgery",
  "Dentistry",
  "Health Sciences"
] # Just the "display_name" of each topic given by Openalex.

# Example of "abstract_inverted_index":
abstract_inverted_index = [
  "Vehicle",
  "density",
  "and",
  "channel",
  "utilization",
  "can",
  "vary",
  "significantly",
  "over",
  "short",
  "time",
  "intervals",
  # ...
]
```

The *abstract inverted index* is not tokenized.

### NB: Reconstruct the abstract

If you kept the original version of the *abstract_inverted_index*,
this is not the case here, you can reconstruct the abstract because
it contains the position of the work in the text.

Example:

```json
{
    "Abstract": [ 0 ],
    ":": [ 1 ],
    "This": [ 2 ],
    "essay": [ 3 ],
    "examines": [ 4 ],
    "the": [ 5, 8, 20 ],
    "requirement": [ 6 ],
    "for": [ 7, 19 ],
    "Marine": [ 9 ],
    "Corps": [ 10 ],
    "to": [ 11 ],
    "formally": [ 12 ],
    "develop": [ 13 ],
    "an": [ 14 ],
    "institutionalized": [ 15 ],
    "safety": [ 16 ],
    "education": [ 17 ],
    "program": [ 18 ],
    "conduct": [ 21 ],
    "of": [ 22 ],
    "live-fire": [ 23 ],
    "ground": [ 24 ],
    "training.": [ 25 ]
}
```

You can reconstruct the abstract from here, which Openalex does,
the result is stored in the value of "TL;DR".

### EOF

