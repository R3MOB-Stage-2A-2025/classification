import json
import re

class JsonParserCrossref:
    def __init__(self, jsonfile: str):
        """
        :param jsonfile: It should be something returned by ``json.dumps()``,
        or in the same format.
        """
        self._publisher: str = ""
        self._DOI: str = ""
        self._type: str = ""
        self._title: str = ""
        self._themes: dict[str, str] = {}
        self._abstractraw: str = "" # The tags are still here.
        self._abstract: str = ""
        self._authors: list[dict] = []

        self._parse_json(jsonfile)

    def _parse_tag(self, textraw: str) -> str:
        """
        :param textraw: something that can have tags like ``<jats:p>``.
        """
        regex_tags: str = r'</?[^>]+>'
        return re.sub(regex_tags, '', textraw)

    def _parse_themes(self, jsondict: dict[str, dict]) -> dict[str, str]:
        themes: dict[str, str] = {}

        if 'container-title' in jsondict:
            themes['container-title'] = jsondict['container-title'][0]

        if 'reference' not in jsondict:
            return themes

        for ref in jsondict['reference']:
            if 'article-title' in ref:
                key: str = ref['key'] + '-article-title'
                themes[key] = ref['article-title']

            if 'journal-title' in ref:
                key: str = ref['key'] + '-journal-title'
                themes[key] = ref['journal-title']

        return themes

    def _parse_json(self, jsonraw: str) -> dict[str, dict]:
        #try:
        jsondict: dict[str, dict] = json.loads(jsonraw)

        self._publisher = jsondict['publisher']
        self._DOI = jsondict['DOI']
        self._type = jsondict['type']
        self._title = jsondict['title'][0]
        self._authors = jsondict['author']
        self._themes = self._parse_themes(jsondict)

        if 'abstract' not in jsondict:
            return jsondict

        self._abstractraw = jsondict['abstract']
        self._abstract = self._parse_tag(jsondict['abstract'])
        #except:
            #print(f'An error occured!')

        return jsondict

    def publisher(self) -> str:
        return self._publisher

    def DOI(self) -> str:
        return self._DOI

    def type(self) -> str:
        return self._type

    def title(self) -> str:
        return self._title

    def themes(self) -> str:
        return self._themes

    def abstractraw(self) -> str:
        """
        Get the abstract with the original tags like ``<jats:p>``.
        """
        return self._abstractraw

    def abstract(self) -> str:
        return self._abstract

    def authors(self) -> list[dict]:
        return self._authors

    def classify_me(self) -> str:
        """
        :return: a concatenation of every elements that can be
        used to classify the publication.
        """
        concatenation: str = ""

        # Doing like this: ``[title][ theme1=container-title ][...] abstract``.
        concatenation += "[ " + self.title() + " ]"

        themes: dict[str, str] = self.themes()
        for elt in themes.values():
            concatenation += "[ " + elt + " ]"

        concatenation += " " + self.abstract()

        return concatenation

