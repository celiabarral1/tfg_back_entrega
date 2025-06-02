import librosa

class Feature_Extractor:
        
    def get_features(self, audio_file):
        
        features, _ = librosa.load(path=audio_file)
        
        return features