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
    def __init__(self, processingFilepath: str = "./processing/data.json"):
        self.name = "Labellator"

        # <Processing data loader>
        self.processingFilepath = processingFilepath

        if os.path.exists(processingFilepath):
            with open(processingFilepath, 'rt') as prf:
                processingDataJson = json.load(prf)
            self.processingDataDict = processingDataJson
        else:
            self.processingDataDict = {}
        # </Processing data loader>

    def checkpoint_processing(self) -> None:
        """
        To be called when we want to save our progress in the file.

        !! Calling this function will erase the actual content of the file !!
        """

        #text: str = json.dumps(self.processingDataDict)
        #with open(self.processingFilepath, 'w') as pwf:
            #pwf.write(text)

        pwf = open(self.processingFilepath, 'w')

        json.dump(self.processingDataDict, fp=pwf,
                  separators=(",", ":\n"), indent=2)

        pwf.close()

    def store_publication(self, publication: str) -> None:

        parsed_publication_dict = JsonParserCrossref(publication).line_json()
        DOI: str = parsed_publication_dict.get("DOI", "3301")
        OPENALEX: str = parsed_publication_dict.get("OPENALEX", "404N0tF0und!")

        if DOI == "3301":
            print(f'Cant add, the DOI is not here! OPENALEX={OPENALEX}')
            return

        parsed_publication_dict.pop('DOI')

        # <Check> if the publication is already in here.
        if self.processingDataDict.get(DOI, {}) != {}:
            print(f'DOI={DOI}, OPENALEX={OPENALEX} Already here!')
            return
        # </Check>

        # <Write> the new publication into the processing array.
        self.processingDataDict[DOI] = parsed_publication_dict
        # </Write>

