# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 18:29:46 2021

@author: ekohrt

AtomicCards.json from the MTGJson project is too big to put on github.
It also has a lot of unnecessary data in it. 
This code creates a new smaller file with just the important information.

"""

import json

with open('AtomicCards.json', encoding='utf-8') as json_file:
    cards_dict = json.load(json_file)


newJsonObject = {'data': {}}
for card in cards_dict['data'].keys():
    cardEntry = cards_dict['data'][card]
    newFaces = []
    for idx, face in enumerate(cardEntry):
        faceData = {}
        if 'manaCost' in cards_dict['data'][card][idx].keys():
            faceData['manaCost'] = cards_dict['data'][card][idx]['manaCost']
        if 'type' in cards_dict['data'][card][idx].keys():
            faceData['type'] = cards_dict['data'][card][idx]['type']
        if 'legalities' in cards_dict['data'][card][idx].keys():
            faceData['legalities'] = cards_dict['data'][card][idx]['legalities']
        if 'text' in cards_dict['data'][card][idx].keys():
            faceData['text'] = cards_dict['data'][card][idx]['text']
        if 'printings' in cards_dict['data'][card][idx].keys():
            faceData['printings'] = cards_dict['data'][card][idx]['printings']
        if 'types' in cards_dict['data'][card][idx].keys():
            faceData['types'] = cards_dict['data'][card][idx]['types']
        
        newFaces.append(faceData)
    newJsonObject['data'][card] = newFaces
    
jsonString = json.dumps(newJsonObject, indent=4, sort_keys=True)
print(jsonString[:10000])
with open("AtomicCards_Small.json", 'w') as fp:
        json.dump(newJsonObject, fp)
print("File 'AtomicCards_Small.json' created.")