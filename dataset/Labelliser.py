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
        pwf = open(self.processingFilepath, 'w')

        json.dump(self.processingDataDict, fp=pwf,
                  separators=(",", ":\n"), indent=2)

        pwf.close()

    def store_publication(self, publication: str = None, labels: str = None) -> None:
        """
        This function can store a publication or can store labels
            of the publication. It can do both.

        :param publication: a publication that is in the *Crossref style*
            and comes from `json.dumps()`.

            Example: See the *Retriever* module.

            If publication == None, then it will be in the "label storage"
                mode.

        :param labels: labels from the *Classifier* module.
            Example:
            ```
            {'DOI': '10.1007/978-3-030-04915-7_62', 'challenges': '["Technologiques", "Economiques"]', 'themes': '[ "Other" ]', 'scientificThemes': '["Mat\\u00e9riaux, A\\u00e9rodynamique, Transition \\u00e9cologique, \\u00c9nerg\\u00e9tique et Mobilit\\u00e9s durables", "Sciences cognitives, Interfaces H/M", "Base et Traitement de donn\\u00e9es, IA"]', 'mobilityTypes': '["Fluvial/Maritime"]', 'axes': '["Accompagner le d\\u00e9veloppement des syst\\u00e8mes de transports d\\u00e9carbon\\u00e9s et s\\u00fbrs"]', 'usages': '[ "Other" ]'}
            ```

            If labels == None, then it will be in the "publication storage"
                mode.
        """

        if publication != None:
            parsed_publication_dict = JsonParserCrossref(publication).line_json()
        elif labels != None:
            parsed_publication_dict = json.loads(labels)
        else:
            return

        DOI: str = parsed_publication_dict.get("DOI", "3301")
        OPENALEX: str = parsed_publication_dict.get("OPENALEX", "404N0tF0und!")

        if DOI == "3301" or DOI == "" or DOI == None:
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

    def related(self, publication: str) -> None:
        """
        It stores locally the related papers from *Openalex* of the
        given publication. It will store it in `self.processingDataDict`,
        which is written in the output file using the function
        `self.checkpoint_processing()` (you need to call it manually).

        Example: See in the `dataset/raw/` directory.

        :param publication: a publication that is in the *Crossref style*
            and comes from `json.dumps()`.
        """
        parsed_publication = JsonParserCrossref(publication)

        # <ID>
        parsed_publication_ID = parsed_publication.ID()
        DOI: str = parsed_publication_ID.get("DOI", "3301")
        OPENALEX: str = parsed_publication_ID.get("OPENALEX", "404N0tF0und!")
        # </ID>

        # <Similarities>
        parsed_publication_similarities = parsed_publication.similarities()
        parsed_publication_related =\
            parsed_publication_similarities.get("related", [])

        for i in range(len(parsed_publication_related)):
            current: str =\
                parsed_publication_related[i].get("OPENALEX", "")

            if current != "":
                parsed_publication_related[i] = current

        related: list[str] = parsed_publication_related
        # </Similarities>

        if DOI == "3301":
            print(f'Cant add, the DOI is not here! OPENALEX={OPENALEX}')
            return

        # <Check> if the publication is already in here.
        if self.processingDataDict.get(DOI, {}) != {}:
            print(f'DOI={DOI}, OPENALEX={OPENALEX} Already here!')
            return
        # </Check>

        # <Write> the new publication into the processing array.
        self.processingDataDict[DOI] = related
        # </Write>

