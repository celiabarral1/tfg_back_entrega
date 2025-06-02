"""
author='Alberto Gallucci Suárez'
author_email='albertogalluccis@gmail.com'
url='https://www.linkedin.com/in/alberto-gallucci-suárez/'
"""

import json
import os
import pandas
import csv
import pickle

from models.labels_functions import labels_json, unified_labels
from sklearn.calibration import LabelEncoder


def write_json(data, filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            datos = json.load(f)
    else:
        datos = []

    datos.append(data)

    with open(filename, 'w') as f:
        json.dump(datos, f, indent=4)
        

def load_csv(filename):
    data = pandas.read_csv(filename)
    if 'Unnamed: 0' in data.columns:
        data.drop('Unnamed: 0', axis=1, inplace=True)

    return data

def write_csv(data, filename, mode):
    with open(filename, mode, encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)


def load_obj(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


def reformat_label(label, dataname):
    each_target = dict(labels_json[dataname])

    each_target = list(each_target.keys())

    label = each_target[label]
    return unify_label(label)

def decode_label(label, dataname):
    lab_enc = LabelEncoder()
    lab_enc.fit_transform(list(labels_json[dataname].keys()))
    label = lab_enc.inverse_transform([label])[0]
    return unify_label(label)


def unify_label(label):
    if label in unified_labels:
        return unified_labels[label]
    else:
        return label
    