import json

# <Parser>
import sys
import os

dir_path_current: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path_current.removesuffix("/dataset") +\
                "/parsing/python/json")

from JsonParserCrossref import JsonParserCrossref
# </Parser>

class Labelliser:
    def __init__(self):
        self.name = "Labellator"

    def store_publication(self, publication: str,
                          filepath: str = "./processing/data.json") -> None:
        parsed_publication_dict = JsonParserCrossref(publication).line_json()
        parsed_publication = json.dumps(parsed_publication_dict)

        DOI: str = parsed_publication_dict.get("DOI", "N0tH3r3!")
        OPENALEX: str = parsed_publication_dict.get("OPENALEX", "N0tH3r3!")

        # <Check> if the publication is already in here.
        # ! Time consuming O(nb_line_file) because of *json* format !
        check = open(filepath, 'r') if os.path.exists(filepath) else []

        for line in check:
            line_dict = json.loads(line)
            line_DOI: str = line_dict.get("DOI", "")
            line_OPENALEX: str = line_dict.get("OPENALEX", "")

            if DOI == line_DOI or OPENALEX == line_OPENALEX:
                print(f'DOI={DOI}, OPENALEX={OPENALEX} Already here!')
                return

        if check != []:
            check.close()
        # </Check>

        with open(filepath, "a") as f:
            f.write(parsed_publication)
            f.write("\n")

