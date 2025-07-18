import os
import re

def find_dois_dataset(filepath: str = './raw/data.json') -> list[str]:
    """
    :return: all the *DOI*'s, as *URL*s from `https://doi.org/`.
    This is a regex finder.

    NB: the returned list could contain the same element multiple times.
    """

    base_url: str = "https://doi.org/"
    regex_doi: str = r'10\.\d{4,9}/[\w.\-;()/:]+'
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
    :return: all the *OPENALEX*'s, as *URL*s from `https://openalex.org/`.
    This is a regex finder.

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

