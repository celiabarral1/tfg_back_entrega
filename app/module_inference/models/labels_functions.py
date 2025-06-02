import os
import re
import pandas as pd

labels_json = {
    'MIXED': {  
        'neu': 0, # Neutral   (DEMOS)
        "gio": 2, # Hapiness  (EMOFILM-es)
        "tri": 3, # Sadness   (EMOFILM-es)
        "rab": 4, # Anger     (EMOFILM-es)
        "ans": 5, # Fear      (EMOFILM-es)
        "dis": 6  # Disgust   (EMOFILM-es)
    },
    'EmoDBSpain':{
        'Neutro':   0, # Neutral
        'Alegria':  2, # Hapiness
        'Tristeza': 3, # Sadness
        'Ira':      4, # Anger
        'Miedo':    5, # Fear
        'Asco':     6, # Disgust
        'Sorpresa': 7  # Surprise
    },
    'MEACorpus':{
        'neutral':  0, # Neutral
        'joy':      2, # Hapiness
        'sadness':  3, # Sadness
        'anger':    4, # Anger
        'fear':     5, # Fear
        'disgust':  6  # Disgust
    }
}

unified_labels = {
    'neu': 'neutral',
    'Neutro': 'neutral',
    'gio': 'happiness',
    'Alegria': 'happiness',
    'joy': 'happiness',
    'tri': 'sadness',
    'Tristeza': 'sadness',
    'rab': 'anger',
    'Ira': 'anger',
    'ans': 'fear',
    'Miedo': 'fear',
    'dis': 'disgust',
    'Asco': 'disgust',
    'Sorpresa': 'surprise',
}