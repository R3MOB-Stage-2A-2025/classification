import json

class JsonParserCrossref:
    def __init__(self, jsonfile: str):
        """
        :param jsonfile: It should be something returned by ``json.dumps()``,
        or in the same format.
        """

        # <Human Readable>
        self._title: str = ""
        self._abstract: str = ""
        # </Human Readable>

        # <Identifiers>
        self._DOI: str = ""
        self._URL: str = ""
        self._OPENALEX: str = ""
        # </Identifiers>

        # <Publisher>
        self._TYPE: str = ""
        self._ISSN: str = ""
        self._publisher: str = ""
        self._container_title: str = ""
        self._container_url: list[str] = []
        self._publication_date: str = ""
        # </Publisher>

        # <People>
        self._author: list[dict] = []
        # </People>

        # <Similarities>
        self._reference: list[dict] = []
        self._related: list[dict] = []
        # </Similarities>

        # <Keywords>
        self._topics: list[dict] = []
        self._keywords: list[dict] = []
        self._concepts: list[dict] = []
        # </Keywords>

        # <Miscellenaous>
        self._sustainable_development_goals: list[dict] = []
        self._abstract_inverted_index: list[dict] = []
        # </Miscellenaous>

        # <Parsing>
        self._parse_json(jsonfile)
        # </Parsing>

    def _parse_topics(self, publication: dict[str, dict]) -> list[str]:
        """
        Just retrieve the *display name*:

        ```
    'topics' : [
    {
        'id' : 'https://openalex.org/T11458',
        'display_name' : 'Advanced Wireless Communication Technologies',
        'score' : 1.0,
        'subfield' : {
            'id' : 'https://openalex.org/subfields/2208',
            'display_name' : 'Electrical and Electronic Engineering'
        },
        'field' : {
            'id' : 'https://openalex.org/fields/22',
            'display_name' : 'Engineering'
        },
        'domain' : {
            'id' : 'https://openalex.org/domains/3',
            'display_name' : 'Physical Sciences'
        }
    },
    {
        ...
        ```
        """

        toto: list[dict] = publication.get("topics", [])
        toto_return: list[str] = []

        for i in range(len(toto)):
            toto_return.append(toto[i].get('display_name', ""))

            toto_return.append(
                toto[i].get('subfield', {})\
                       .get('display_name', "")
            )

            toto_return.append(
                toto[i].get('field', {})\
                       .get('display_name', "")
            )

            toto_return.append(
                toto[i].get('domain', {})\
                       .get('display_name', "")
            )

        return toto_return

    def _parse_keywords(self, publication: dict[str, dict]) -> list[str]:
        """
        same as `self._parse_topics()` but easier!
        """
        keykey: list[dict] = publication.get("keywords", [])
        keykey_result: list[str] = []

        for i in range(len(keykey)):
            keykey_result.append(keykey[i].get('display_name', ""))

        return keykey_result

    def _parse_concepts(self, publication: dict[str, dict]) -> list[str]:
        """
        same as `self._parse_topics()` but easier!
        """
        concepts: list[dict] = publication.get("concepts", [])
        concepts_result: list[str] = []

        for i in range(len(concepts)):
            concepts_result.append(concepts[i].get('display_name', ""))

        return concepts_result

    def _parse_sustainable(self, publication: dict[str, dict]) -> list[str]:
        """
        same as `self._parse_topics()` but easier!
        """
        sus: list[dict] = publication.get("sustainable_development_goals", [])
        sus_result: list[str] = []

        for i in range(len(sus)):
            sus_result.append(sus[i].get('display_name', ""))

        return sus_result

    def _parse_keywords_from_inverted_abstract(self) -> list[str]:
        """
        See *OpenAlex* `abstract_inverted_index`.
        :return: a list of keywords from the abstract.
        """
        if self._abstract_inverted_index != None:
            return list(self._abstract_inverted_index.keys())
        return []

    def _parse_json(self, jsonraw: str) -> dict[str, dict]:
        publication: dict[str, dict] = json.loads(jsonraw)

        # <Human Readable>
        self._title = publication.get('title', [""])[0]
        self._abstract = publication.get('abstract',\
                                  publication.get('TL;DR', ""))
        # </Human Readable>

        # <Identifiers>
        self._DOI = publication.get("DOI", "")
        self._URL = publication.get("URL", "")
        self._OPENALEX = publication.get("OPENALEX", "")
        # </Identifiers>

        # <Publisher>
        self._TYPE = publication.get("type", "")
        self._ISSN = publication.get("ISSN", "")
        self._publisher = publication.get("publisher", "")
        self._container_title = publication.get("container-title", "")
        self._container_url = publication.get("container-url", [])
        self._publication_date = publication.get("publication-date", "")
        # </Publisher>

        # <People>
        self._author = publication.get("author", [])
        # </People>

        # <Similarities>
        self._reference = publication.get("reference", [])
        self._related = publication.get("related", [])
        # </Similarities>

        # <Keywords>
        self._topics = self._parse_topics(publication)
        self._keywords = self._parse_keywords(publication)
        self._concepts = self._parse_concepts(publication)
        # </Keywords>

        # <Miscellenaous>
        self._sustainable_development_goals =\
            self._parse_sustainable(publication)

        self._abstract_inverted_index =\
            publication.get("abstract_inverted_index", {})
        # </Miscellenaous>

        return publication

    def human_readable(self) -> dict[str, str]:
        return {
            "title": self._title,
            "abstract": self._abstract,
        }

    def ID(self) -> dict[str, str]:
        return {
            "DOI": self._DOI,
            "OPENALEX": self._OPENALEX,
            "URL": self._URL,
        }

    def publisher(self) -> dict[str, str | list]:
        return {
            "TYPE": self._TYPE,
            "ISSN": self._ISSN,
            "publisher": self._publisher,
            "container-title": self._container_title,
            "container-url": self._container_url,
            "publication_date": self._publication_date,
        }

    def people(self) -> dict[str, list[dict]]:
        return self._authors

    def similarities(self) -> dict[str, list[str]]:
        return {
            "reference": self._reference,
            "related": self._related,
        }

    def keywords(self) -> dict[str, dict[str, str | int]]:
        return {
            "topics": self._topics,
            "keywords": self._keywords,
            "concepts": self._concepts,
        }

    def miscellenaous(self) -> dict[str, list[str] | dict[str, list[int]]]:
        return {
            "sustainable_development_goals":\
                            self._sustainable_development_goals,
            "abstract_inverted_index":\
                            self._abstract_inverted_index,
        }

    def line_json(self) -> dict[str, str | list[str]]:
        """
        Write the publication in a `json` format, in order to classify it.

        Keys:
        "DOI", "OPENALEX", "title", "abstract", "topics", "given_keywords",
        "concepts", "sustainable_goals"
        """

        elements: dict[str, str | list[str]] = {
            'DOI': self._DOI, # str
            'OPENALEX': self._OPENALEX, # str
            'title': self._title,
            'abstract': self._parse_keywords_from_inverted_abstract(), # list[str]
            'topics': self._topics, # list[str]
            'keywords': self._keywords, # list[str]
            'concepts': self._concepts, # list[str]
            'sustainable': self._sustainable_development_goals # list[str]
        }

        return elements

    def classify_me(self, line_json: dict[str, str | list[str]] = None) -> str:
        """
        :return: a concatenation of every elements that can be
        used to classify the publication.

        The only thing that is not tokenized here is the `title`.
        """

        if line_json == None:
            line_json = self.line_json()
        line_json_dict: dict[str, str | list[str]] = line_json

        concatenation: str = ""
        concatenation += line_json_dict['title']
        concatenation += ", "
        concatenation += ', '.join(line_json_dict['abstract'])
        concatenation += ", "
        concatenation += ', '.join(line_json_dict['topics'])
        concatenation += ", "
        concatenation += ', '.join(line_json_dict['keywords'])
        concatenation += ", "
        concatenation += ', '.join(line_json_dict['concepts'])
        concatenation += ", "
        concatenation += ', '.join(line_json_dict['sustainable'])

        return concatenation

