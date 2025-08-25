import json

# <Parser>
import sys
import os

dir_path_current: str = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir_path_current.removesuffix("/dataset") +\
                "/parsing/python/json")

from JsonParserCrossref import JsonParserCrossref
# </Parser>

label_names: list[str] = [
  "axes",
  "challenges",
  "mobilityTypes",
  "scientificThemes",
  "themes",
  "usages"
]

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
    'label_name (example: challenges, themes, etc..)': [
        { 'categories': ["tech"], 'text': "Once upon a time..." },
        { 'categories': ["business"], 'text': "In the Wilderness..." },
        { 'categories': ["sport"], 'text': "By Hugo Montenegro..." },
        { 'categories': ["sport"], 'text': "And Sergio Leone..." },
        { 'categories': ["entertainment"], 'text': "And Me..." }
    ],
    ...
}
"""

resultJsonDict: dict[str, [dict[str, str | list[str]]]] = {
    label_name: [] for label_name in label_names
}

keysJsonDict: list[str] = textJsonDict.keys()
# </Result Json dictionary>

def construct(label_name: str) -> None:
    for key in keysJsonDict:
        line_json: dict[str, str | list[str]] = textJsonDict.get(key, {})
        text: str =\
            JsonParserCrossref().classify_me(line_json=line_json)

        categories: list[str] = labelJsonDict.get(key, {}).get(label_name, [])

        line_output_file: dict[str, str | list[str]] =\
            { 'categories': categories, 'text': text }

        resultJsonDict[label_name].append(line_output_file)

def save() -> None:
    pwf = open(file_output, 'w')

    json.dump(resultJsonDict, fp=pwf,
              separators=(",", ":\n"), indent=2)

    pwf.close()

if __name__ == '__main__':
    for label_name in label_names:
        construct(label_name)

    save()

