import os
import re
import json

def find_dois_dataset(filepath: str = './raw/data.json') -> list[str]:
    """
    :param filepath: The input file.
    :return: all the *DOI*'s, as *URL*s from `https://doi.org/`.
    This is a regex finder, here is the regex: `r'10\.\d{4,9}/[\w.\-;()/:]+'`.

    NB: the returned list could contain the same element multiple times.
    """

    base_url: str = "https://doi.org/"
    regex_doi: str = r'10\.\d{4,9}/[\w.\-;()/:]+'
    #regex_doi: str = r'10\.\d{4,9}/[^\s]+'
    result: list[str] = []

    check = open(filepath, 'r') if os.path.exists(filepath) else []

    for line in check:
        line_dois: list[str] = re.findall(regex_doi, line)
        url_line_dois: list[str] = []

        for i in range(len(line_dois)):
            url_line_doi: str = base_url + line_dois[i]
            url_line_dois.append(url_line_doi)

        if line_dois != None:
            result.extend(url_line_dois)

    if check != []:
        check.close()

    return result

def find_openalex_dataset(filepath: str = './raw/data.json') -> list[str]:
    """
    :param filepath: The input file.
    :return: all the *OPENALEX*'s, as *URL*s from `https://openalex.org/`.
    This is a regex finder, here is the regex:
        `r'"https:\/\/openalex\.org\/W\d+"'`.

    NB: the returned list could contain the same element multiple times.
    """

    regex_openalex: str = r'"https:\/\/openalex\.org\/W\d+"'
    result: list[str] = []

    check = open(filepath, 'r') if os.path.exists(filepath) else []

    for line in check:
        line_openalex: list[str] = re.findall(regex_openalex, line)

        if line_openalex != None:
            result.extend(line_openalex)

    if check != []:
        check.close()

    return result

class MetadataRetriever:
    def __init__(self, processingFilepath: str = './processing/data.json'):
        """
        This class has the purpose of storing the file from the `processing/`
            dir, in order to give it to the *Classifier* module by
            `labelling.py`, without having to reload every time the file.

        :param processingFilepath: the input file.
        """
        self.name = "MetadataRetriever"

        # <Processing data loader>
        self.processingFilepath = processingFilepath

        if os.path.exists(processingFilepath):
            with open(processingFilepath, 'rt') as prf:
                processingDataJson = json.load(prf)
            self.processingDataDict = processingDataJson
        else:
            self.processingDataDict = {}
        # </Processing data loader>

    def retrieve_data_from_doi(self, doi: str) -> dict[str, str | dict[str]]:
        """
        Given a DOI, it retrieves the specific publication metadatas
            in constant time, stored in `self.processingDataDict[doi]`.
        """
        return self.processingDataDict[doi]

