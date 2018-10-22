#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic example for a bot that uses inline keyboards.

# This program is dedicated to the public domain under the CC0 license.
"""
import re

locations = {'location-1': {'name': 'greece',
                            'schools': [{'uuid': 'd3d8bac4-1ac8-4e7c-891e-03168eff7226', 'name': '46ο Δημοτικό Σχολείο Πατρών'},
                                        {'uuid': 'f065a043-5fb0-454f-bf3f-bbdcb3926fce', 'name': '8ο Γυμνάσιο Βόλου'},
                                        {'uuid': '2951e56d-ad8f-4ea6-bf4d-4f6d46060ab0', 'name': 'Πειραματικό Δημοτικό Σχολείο Πανεπιστημίου Πατρών'},
                                        {'uuid': '8eb0b364-af94-4536-aa5b-12ccf4549e1f', 'name': 'Γυμνάσιο Πενταβρύσου Καστοριάς'},
                                        {'uuid': '79a262dc-e0ca-4ce4-80f3-73afe2a6a1d4', 'name': '2ο Δημοτικό Σχολείο Παραλίας Πατρών'},
                                        {'uuid': '107beec7-859b-4d49-8da7-fbccd39188db', 'name': 'Πειραματικό Γυμνάσιο Πατρών'},
                                        {'uuid': 'f7e14a41-6358-4d48-be6e-28145c16ffa3', 'name': 'Δημοτικό Σχολείο Λυγιάς'},
                                        {'uuid': 'a138ad38-0a48-46e6-b15b-e95ee70af3ea', 'name': '1ο Γυμνάσιο Ν. Φιλαδέλφειας'},
                                        {'uuid': '0876e4a2-9e1a-4fc3-b04a-ff19dff1314b', 'name': '8ο Γυμνάσιο Πατρών'},
                                        {'uuid': 'a63e16b7-84b7-4c46-bb0d-29443a7cce13', 'name': '2o Γυμνάσιο Ν. Ιωνίας'},
                                        {'uuid': '672b3677-4981-42b7-bacf-bd87e42f547a', 'name': '1o Δημοτικό Σχολείο Ψυχικού Αττικής'},
                                        {'uuid': '1e443c40-2090-4ee1-82f2-554fd29219d8', 'name': '1ο Επαγγελματικό Λύκειο Πατρών'},
                                        {'uuid': '1d200eb3-9533-461d-8929-17c75bd0f470', 'name': '5ο Δημοτικό Σχολείο Νέας Σμύρνης'},
                                        {'uuid': '2d930a5f-6819-4815-a126-0825294fee62', 'name': '3o ΓΕΛ Ν. Φιλαδέλφειας'},
                                        {'uuid': '1614db70-b727-47aa-99bf-bbb228f1fed2', 'name': 'Δημοτικό Σχολείο Φιλοθέης'},
                                        {'uuid': '4b5d3819-aa82-4e69-86ca-990c32668ee3', 'name': 'Πειραματικό Γυμνάσιο Πανεπιστημίου Πατρών'},
                                        {'uuid': '4e76caa6-90a2-4d81-a0f8-7d7e18406e8f', 'name': '1o Γυμνάσιο Ραφήνας'},
                                        {'uuid': 'ec51bc2e-ec3a-41e3-8ef8-60fc3bbe0226', 'name': '1ο Εργαστηριακό Κέντρο Πατρών'},
                                        {'uuid': 'bcb7d3d5-ad05-46fa-9a8d-42cc5dbaf34b', 'name': 'Talos'},
                                        {'uuid': 'b70e0ce2-7f6c-4c30-8159-92be56230fff', 'name': '6ο Δημοτικό Σχολείο Καισαριανής'},
                                        {'uuid': '9728d857-7fd7-444e-96f4-def7137c837c', 'name': 'Ελληνογερμανική Αγωγή'},
                                        {'uuid': 'e7103f6a-67f6-4f4a-95df-2566df48c0e4', 'name': 'Δημοτικό Σχολείο Μεγίστης'},
                                        {'uuid': '3bf1856a-1a61-4db1-a40a-dd217116370f', 'name': 'Πειραματικό Λύκειο Πανεπιστημίου Πατρών'}
                                        ]},
             'location-2': {'name': 'sweeden', 'schools': [{'uuid': 'a1b8fc98-675f-4302-a007-cb67e4863477', 'name': 'Soderhamn'}, ]},
             'location-3': {'name': 'italy',
                            'schools': [{'uuid': 'd3537dbe-7123-4986-993c-fa1a44f76b08', 'name': 'Gramsci-Keynes School'},
                                        {'uuid': '7cd850f5-2096-44ac-a404-78972f67b10c', 'name': 'Sapienza'}]}}

schoolNames = []
for item in locations['location-1']['schools']:
    schoolNames.append(item)
for item in locations['location-2']['schools']:
    schoolNames.append(item)
for item in locations['location-3']['schools']:
    schoolNames.append(item)


def getSchoolStrId(id):
    return id.replace('school-', '')

def getSchoolNameFromId(uuid):
    return [item for item in schoolNames if item["uuid"] == getSchoolStrId(uuid)][0]["name"]


def getSiteProperties(s, group_uuid):
    properties = []
    resources = s.groupResources(group_uuid)
    print "resources", len(resources)
    for resource in resources:
        # TODO: add + group_uuid
        if resource['systemName'].startswith('site-'):
            properties.append(
                {'resourceUuid': resource['uuid'], 'systemName': resource['systemName'],
                 'property': s.phenomenonByUuid(resource['phenomenonUuid'])['name'].lower()})
    return properties


def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def findResource(resources, textList):
    for r in resources:
        if "external" not in r['property']:
            for text in textList:
                if findWholeWord(text)(r['property']):
                    return r
    for r in resources:
        for text in textList:
            if findWholeWord(text)(r['property']):
                return r
    return None
