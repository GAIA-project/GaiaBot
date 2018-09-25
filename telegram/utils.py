#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Basic example for a bot that uses inline keyboards.

# This program is dedicated to the public domain under the CC0 license.
"""
import re

locations = {'location-1': {'name': 'Greece',
                            'schools': [{'id': 19640, 'name': "Γυμνάσιο Πενταβρύσου Καστοριάς"},
                                        {'id': 156886, 'name': "1ο Επαγγελματικό Λύκειο Πατρών"},
                                        {'id': 155877, 'name': "2ο Δημοτικό Σχολείο Παραλίας Πατρών "},
                                        {'id': 27827, 'name': "8ο Γυμνάσιο Πατρών"},
                                        {'id': 506265, 'name': "1o Δημοτικό Σχολείο Ψυχικού Αττικής"},
                                        {'id': 141587, 'name': "1o Γυμνάσιο Ραφήνας"},
                                        {'id': 144024, 'name': "Δημοτικό Σχολείο Λυγιάς"},
                                        {'id': 155851, 'name': "5ο Δημοτικό Σχολείο Νέας Σμύρνης"},
                                        {'id': 157185, 'name': "Ελληνογερμανική Αγωγή"},
                                        {'id': 144242, 'name': "1ο Γυμνάσιο Ν. Φιλαδέλφειας"},
                                        {'id': 141611, 'name': "Πειραματικό Γυμνάσιο Πατρών"},
                                        {'id': 204, 'name': "Πειραματικό Γυμνάσιο Πανεπιστημίου Πατρών"},
                                        {'id': 195, 'name': "Πειραματικό Λύκειο Πανεπιστημίου Πατρών"},
                                        {'id': 3206, 'name': "Πειραματικό Δημοτικό Σχολείο Πανεπιστημίου Πατρών"},
                                        {'id': 155877, 'name': "2ο Δημοτικό Σχολείο Παραλίας Πατρών"},
                                        {'id': 155849, 'name': "6ο Δημοτικό Σχολείο Καισαριανής"},
                                        {'id': 155865, 'name': "46ο Δημοτικό Σχολείο Πατρών"},
                                        {'id': 144243, 'name': "Δημοτικό Σχολείο Μεγίστης"},
                                        {'id': 157089, 'name': "1ο Εργαστηριακό Κέντρο Πατρών"}]},
             'location-2': {'name': 'Sweden', 'schools': [{'id': 159705, 'name': "Soderhamn"}, ]},
             'location-3': {'name': 'Italy',
                            'schools': [{'id': 155076, 'name': "Gramsci-Keynes School"},
                                        {'id': 155077, 'name': "Sapienza"}]}}

schoolNames = []
for item in locations['location-1']['schools']:
    schoolNames.append(item)
for item in locations['location-2']['schools']:
    schoolNames.append(item)
for item in locations['location-3']['schools']:
    schoolNames.append(item)


def getSchoolStrId(id):
    return id.replace('school-', '')


def getSchoolIntId(id):
    return int(getSchoolStrId(id))


def getSchoolNameFromId(id):
    return [item for item in schoolNames if item["id"] == getSchoolIntId(id)][0]["name"]


def getSiteProperties(s, idStr):
    properties = []
    resources = s.siteResources({'id': getSchoolIntId('school-' + idStr)})
    for resource in resources:
        if resource['uri'].startswith('site-' + idStr):
            properties.append(
                {'resourceId': resource['resourceId'], 'uri': resource['uri'],
                 'property': resource['property'].lower()})
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
