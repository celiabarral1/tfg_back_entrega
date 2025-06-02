import os
import numpy as np
from time import sleep

from app.module_inference.infere_emotion.test import check_installation
from app.module_inference.infere_emotion.mqtt import config_mqtt, mandar_alerta_emocion

from app.module_inference.models.models import Pretrained_Model_Dimensional, load_model

from utils.utils import load_csv, reformat_label, write_csv, decode_label, write_json

from features_extraction.extract_features_w2v2 import Feature_Extractor as fe_w2v2
from features_extraction.extract_features_ours import Feature_Extractor as fe_ours
from features_extraction.extract_features_pretrained import Feature_Extractor as fe_pre


#   Predict the emotions of each features group
def get_emotions(models, features, mode="hard"):
    predictions = []
    
    if(mode == "hard"):
        if 'dict' in str(type(models)):
            features = models['scaler'].transform(features)
            for model in models['models']:
                prediction = model.predict(features)
                predictions.append(list(prediction))
            
            predictions = np.array(predictions, dtype=object)
            
            unique_elements, counts = np.unique(predictions, return_counts=True)
            final_result =  unique_elements[np.argmax(counts)].item()
        else:
            final_result = int(models.predict(features))
            
        return final_result
            
    elif (mode == "soft"):
        if 'dict' in str(type(models)):
            features = models['scaler'].transform(features)
            for model in models['models']:
                prediction = model.predict_proba(features)
                predictions.append(prediction)
            
            final_result = np.mean(predictions, axis=0)
            final_std = np.std(predictions, axis=0)
        else:
            final_result = models.predict_proba(features)
            final_std = [[0]]
            
        final_result = final_result[0]
        final_std = final_std[0]
            
        return final_result, final_std


def get_dimensional(audio_file):
    
    # features = fe_pre().get_features(audio_file)
    
    model = Pretrained_Model_Dimensional()
    
    values = model.predict(audio_file)
    
    return values


#   Test a model with an audio
def interfere_emotion(dataset_name, audio_file, feature_loader, model, type, csvfile, original_emotion = None, worker_id = None):
    #   Create the header of the .csv including the target column
    if not os.path.exists(csvfile):
        cabeceraCsv = ["file_name", "Emotion_1_label", "Emotion_1_mean", "Emotion_1_std", "Emotion_2_label", "Emotion_2_mean", "Emotion_2_std", "Emotion_3_label", "Emotion_3_mean", "Emotion_3_std", "valence", "arousal", "dominance"]
        
        if original_emotion:
            cabeceraCsv.append('original_emotion')
        else:
            cabeceraCsv.append('user_id')
            cabeceraCsv.append('timestamp')
            
        
        write_csv(cabeceraCsv, csvfile, 'a')
    
    
    features = feature_loader.get_features(audio_file)

    # Get emotions
    porAccuracy, std = get_emotions(model, features, "soft")
    label = get_emotions(model, features, "hard")
        
    dimensional_values = get_dimensional(audio_file)
    
    # Get the indices that would sort the array
    sorted_indices = np.argsort(porAccuracy)[-3:][::-1]
 
    # data = [audio_file.split('/')[-1]]

    data = [os.path.basename(audio_file)]
    print(data)
    
    json_data = {
        "emocategoric": [],  
        "emodimensional": { 
            "valence": float(dimensional_values[0]),  
            "arousal": float(dimensional_values[1]),  
            "dominance": float(dimensional_values[2]) 
        } 
    }
    
    if type == 'pretrained':
        label = decode_label(label, dataset_name)
        for index in sorted_indices:
            emo = decode_label(index, dataset_name)
            prob = porAccuracy[index]
            data.append(emo)
            data.append(prob)
            data.append(0)
            
            json_data['emocategoric'].append({ 
                "emo": emo,  
                "prob": prob
            })
                    
    else:   
        label = reformat_label(label, dataset_name)
        for index in sorted_indices:
            emo = reformat_label(index, dataset_name)
            prob = porAccuracy[index]
            
            data.append(emo)
            data.append(prob)
            data.append(std[index])
            
            json_data['emocategoric'].append({ 
                "emo": emo,  
                "prob": prob
            })
        
    data.append(dimensional_values[0])  
    data.append(dimensional_values[1])  
    data.append(dimensional_values[2])
    
    if original_emotion:
        data.append(original_emotion)
    else:
        timestamp = audio_file.split('/')[-1].split('_')[0]
        data.append(worker_id)
        data.append(timestamp)
            
    #Add to the csv the new data
    write_csv(data, csvfile, 'a')
    
    return json_data

    
def process_audio_files(dataset_name, audio_folder, model, type, csvfile, used_audio_folder, seconds, test):
    
    if type == 'pretrained':
        feature_loader = fe_pre()
    elif type == 'w2v2':
        feature_loader = fe_w2v2()
    else:
        feature_loader = fe_ours(model['mfcc'][0], model['mfcc'][1])
        
        
    if test:
        audio_files = os.listdir(audio_folder)
        
        for audio_file in audio_files:
            audio = os.path.join(audio_folder, audio_file)
            
            if os.path.isfile(audio):
                original_emotion = audio_file.split('_')[0]
                interfere_emotion(dataset_name, audio, feature_loader, model, type, csvfile, original_emotion = original_emotion)
        
        test_csv = load_csv(f'{audio_folder}/../sample_result.csv')
        result_csv = load_csv(csvfile)
        check_installation(audio_folder, test_csv, result_csv)
    
    else:
        
        client = config_mqtt()
        
        while True:
            # List all files in the folder
            audio_files = os.listdir(audio_folder)
            
            for audio_file in audio_files:
                audio = os.path.join(audio_folder, audio_file)
                if os.path.isfile(audio):
                    worker_id = audio_file.split('_')[1].removesuffix('.wav')
                    # Get emotions from audio file
                    data = interfere_emotion(dataset_name, audio, feature_loader, model, type, csvfile, worker_id=worker_id)
                    
                    data['worker_id'] = worker_id
                    write_json(data, csvfile.replace('csv', 'json'))
                    mandar_alerta_emocion(client, data, audio_file.split('_')[0])

                    # Move audio file to other folder
                    os.rename(audio, os.path.join(used_audio_folder, audio_file))
                    
            # Schedule the function to run again after 'seconds' seconds
            sleep(seconds)


def test_folder(audio_folder, model_name, model_folder, csv_folder, seconds, test = False):
    
    dataset_name = model_name.split("_")[-1].split('.')[0]
    used_audio_folder = f'{audio_folder}/../output-audios-used'
    
    # Create .csv for the results
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)

    if test:
        csvfile = f'{csv_folder}/{model_name.removesuffix(".pkl")}-output.csv'
    else:    
        csvfile = f'{csv_folder}/{model_name.removesuffix(".pkl")}-output.csv'

    if not os.path.exists(used_audio_folder):
        os.makedirs(used_audio_folder)
    
        
    model, type = load_model(model_folder, model_name)
        
    # Start the initial processing
    process_audio_files(dataset_name, audio_folder, model, type, csvfile, used_audio_folder, seconds, test)