import json

# <Parser>
import sys
import os

dir_path_current: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path_current.removesuffix("/dataset") +\
                "/parsing/python/json")

from JsonParserCrossref import JsonParserCrossref
# </Parser>

file_with_text: str = './processing/data_depth_3.json'
file_with_label: str = './labelled/data_depth_3.json'
file_output: str = './ready_to_classify/data_depth_3.json'

# <Text data loader>
textJsonDict: dict[str, dict[str, str]] = {}

if os.path.exists(file_with_text):
    with open(file_with_text, 'rt') as prf:
        textJsonDict = json.load(prf)
# </Text data loader>

# <Label data loader>
labelJsonDict: dict[str, dict[str, list[str]]] = {}

if os.path.exists(file_with_label):
    with open(file_with_label, 'rt') as prf:
        labelJsonDict = json.load(prf)
# </Label data loader>

# <Result Json dictionary>
"""
The output file will be a json file:
{
    {
  "10.3390/su15086429": {
    "text": "Impact Assessment of Climate Mitigation Finance on Climate ..."
    "challenges": "[\"Economiques\"]",
    "themes": "[ \"Other\" ]",
    "scientificThemes": "[\"Sciences \\u00e9conomique, \\u00c9valuation des ...",
    "mobilityTypes": "[ \"Other\" ]",
    "axes": "[ \"Other\" ]",
    "usages": "[ \"Other\" ]"
    },
    # ...
}
"""

def construct() -> dict[str, dict[str, str | list[str]]]:
    resultJsonDict = {}

    for doi in labelJsonDict:
        publication: dict[str | list[str]] = labelJsonDict[doi]

        line_json: dict[str, str | list[str]] = textJsonDict.get(doi, {})
        text: str =\
            JsonParserCrossref().classify_me(line_json=line_json)

        publication['text'] = text
        resultJsonDict[doi] = publication

    return resultJsonDict

def save(resultJsonDict) -> None:
    pwf = open(file_output, 'w')

    json.dump(resultJsonDict, fp=pwf,
              separators=(",", ":\n"), indent=2)

    pwf.close()

if __name__ == '__main__':
    resultJsonDict: dict[str, dict[str, str | list[str]]] = construct()
    save(resultJsonDict)

