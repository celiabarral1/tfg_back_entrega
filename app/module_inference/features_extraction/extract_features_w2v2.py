import audonnx
import audinterface

class Feature_Extractor:
    
    def __init__(self):
        self.model = self.load_model()
    
    def load_model(self):
        model_root = './data/models/w2v2_extractor'

        model = audonnx.load(model_root)
        
        return model
        
    def get_features(self, audio_file):
        
        hidden_states = audinterface.Feature(
            self.model.labels('hidden_states'),
            process_func=self.model,
            process_func_args={
                'outputs': 'hidden_states',
            },
            sampling_rate=16000,    
            resample=True,    
            num_workers=5,
            verbose=True,
        )

        features = hidden_states.process_files([audio_file])
        
        return features