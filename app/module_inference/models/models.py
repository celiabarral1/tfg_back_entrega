import audonnx
import audinterface
import numpy as np
import torch.nn.functional as F
import torch
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2Processor
from utils.utils import load_obj
import os

def load_model(model_path, model_name):
    if 'pretrained' in model_path:
        type = 'pretrained'
        model = Pretrained_Model_Categorical(model_path, model_name)
    elif 'w2v2' in model_name:
        type = 'w2v2'
        model = load_obj(model_path + model_name)
    else:
        type = 'ours'
        model = load_obj(model_path + model_name)
    return model, type

class Pretrained_Model_Categorical:
    
    def __init__(self, model_path, model_name):
        self.model, self.processor = self.load_model(model_path, model_name)

    
    def load_model(self, model_path, model_name):
        # Initialize the model
        model = Wav2Vec2ForSequenceClassification.from_pretrained(model_path + model_name)
        processor = Wav2Vec2Processor.from_pretrained(model_path + 'processor')

        # Set the model to evaluation mode
        model.eval()
        
        return model, processor
        
    def predict(self, features):
        self.model.eval()
        # Load and preprocess the audio file
        inputs = self.processor(features.squeeze(), sampling_rate=16000, return_tensors="pt", padding=True)
        with torch.no_grad():
            logits = self.model(inputs.input_values.to('cpu')).logits
        predicted_ids = torch.argmax(logits, dim=-1).item()
        
        return predicted_ids
    
    def predict_proba(self, features):
        probabilities_list = []
        
        inputs = self.processor(features.squeeze(), sampling_rate=16000, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1)
            probabilities_list.append(probabilities)

        return probabilities_list[0].tolist()
    
    
    
class Pretrained_Model_Dimensional:
    
    def __init__(self):
        model_path = './data/models/w2v2_extractor'
        self.model = self.load_model(model_path)

    
    def load_model(self, model_path):
        model = audonnx.load(model_path)
        np.random.seed(0)

        sampling_rate = 16000
        signal = np.random.normal(
            size=sampling_rate,
        ).astype(np.float32)

        model(signal, sampling_rate)
        
        # Initialize the model
        model = audinterface.Feature(
            model.labels('logits'),
            process_func=model,
            process_func_args={
                'outputs': 'logits',
            },
            sampling_rate=sampling_rate,
            resample=True,    
            verbose=True,
        )
        
        return model
        
    def predict(self, file):
        result = self.model.process_file(file)
        result = result.reset_index()
        result = result.iloc[0]
        
        return [result['valence'], result['arousal'], result['dominance']]
    
# class Pretrained_Model_Dimensional:
    
#     def __init__(self, model_path):
#         self.model, self.processor = self.load_model(model_path)

    
#     def load_model(self, model_path):
#         # Initialize the model
#         model = Wav2Vec2ForSequenceClassification.from_pretrained(model_path)
#         processor = Wav2Vec2Processor.from_pretrained(model_path)
        
#         return model, processor
        
#     def predict(self, features):
#         self.model.eval()
        
#         # Load and preprocess the audio file
#         inputs = self.processor(features, return_tensors="pt", padding="longest")
        
#         with torch.no_grad():
#             predictions = self.model(inputs).logits
        
#         return predictions
