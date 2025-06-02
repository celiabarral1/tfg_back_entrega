# Import Libraries
import math
import numpy as np, pandas as pd
from features_extraction.features import cepstral_features, prosodic_features

# Main package for working with audio data
import librosa, librosa.display

class Feature_Extractor():
    def __init__(self, n_mfcc, n_fft):
        self.n_mfcc = n_mfcc
        self.n_fft = n_fft
        
    # 1. Preprocessing
    def preprocess_audio_signal(self, audio_signal, **kwargs):
        alpha = [0.95, 0.97]    
        normalized_audio_signal = kwargs.get("normalized_audio_signal")
        emphasized_audio_signal = kwargs.get("emphasized_audio_signal")
        teagerEO_audio_signal = kwargs.get("teagerEO_audio_signal")
        audio_signal_prp = np.array([])
        
        if normalized_audio_signal:
            audio_signal_prp  = audio_signal / np.max(np.abs(audio_signal))
            
        if emphasized_audio_signal:
            #The pre-emphasis filter can be applied to a signal x  using the first order filter in the following equation:
            # y(t)=x(t)−αx(t−1)
            audio_signal_prp = np.append(audio_signal[0], audio_signal[1:] - alpha[1] * audio_signal[:-1])  
    
        if teagerEO_audio_signal:
                
            # y(t)=x^2(t)−x(t-1)x(t+1)
            #vectorized
            audio_signal_prp = audio_signal.copy()
            audio_signal_prp[1:-1] = audio_signal[1:-1]**2 - audio_signal[:-2]*audio_signal[2:]   

                
        return audio_signal_prp

    # 2-3. Framing and Windowing
    def frameW_audio_signal(self, audio_signal, sample_rate = None, frame_size=0.025,  hop_length=0.01, framing = True):
        """
        Transform a signal into a series of overlapping frames.
        Frame the signal into 20–40 ms frames. with 50% (+/- 10%) overlap between consecutive frames. 
        pupular settings are 25 ms for the frame size, frame_size =0.025 and a 10 ms stride (15 ms overlap)
        This means the frame length for a 16kHz signal is 0.025*16000 = 400 samples with a sample hop length of 160 samples.
        Args:
            audio_signal (array)             : a mono audio signal (Nx1) from which to compute features.
                                                    Should take an emphasided or pre-processed signal
            audio_signal_sample_rate (int)   : the sampling frequency of the signal we are working with.
                                                    Number of samples per second. Default is 16000.
            frame_size, win_len    (float)   : Frame length in sec.
                                                    Default is 0.025.
            frame_stride or win_hope (float) : step between successive windows or frames in sec.
                                                    Default is 0.01.

        Returns:
            array of frames.
            frame length.
        """  
        audio_signal_length = len(audio_signal)
        
        if frame_size == audio_signal_length or not framing:
            return audio_signal.reshape(1, -1)
        if frame_size < 0 or hop_length<0:
            print ("Invalid hop_length or frame_size. Negative numbers not accepted.")   
        # check if frame_size is given in milliseconds in decimal values
        if 0 < frame_size <=1:        
            # compute frame length and frame step (convert from seconds to samples)
            frame_size = int(round(frame_size * sample_rate)) if  int(round(frame_size * sample_rate)) > 0 else len(audio_signal) 
        # check if hop_length is given in decimal values
        if 0< hop_length <=1:
            hop_length = int(round(hop_length * sample_rate))
            #frames_overlap = frame_size - frame_step
        
        if frame_size < hop_length:
            print ("Invalid hop_length or frame_size. Hope lentgh cannot be bigger than frame size.")
        
        # PRE PROCESSING
        audio_signal = self.preprocess_audio_signal(audio_signal, emphasized_audio_signal =True )
        #FRAMING
        
        # Make sure that we have at least 1 frame+
        num_frames = np.abs(audio_signal_length - frame_size) // hop_length
        rest_samples = np.abs(audio_signal_length - frame_size) % hop_length

        # Pad Signal to make sure that all frames have equal number of samples
        # without truncating any samples from the original signal
        if rest_samples != 0:
            pad_signal_length = int(hop_length - rest_samples)
            z = np.zeros((pad_signal_length))
            pad_signal = np.append(audio_signal, z)
            num_frames += 1
        else:
            pad_signal = audio_signal

        # compute indices
        idx1 = np.tile(np.arange(0, frame_size), (num_frames, 1))
        idx2 = np.tile(np.arange(0, num_frames * hop_length, hop_length),
                        (frame_size, 1)).T
        indices = idx1 + idx2
        frames = pad_signal[indices.astype(np.int32, copy=False)]
        
        #WINDOWING
        windowed_frames = frames*np.hamming(frame_size)
        
        return windowed_frames
        

    # 5. Extract Features

    def extract_feature_ours(self, audio_signal, sample_rate, **kwargs):
        """
        Extract feature from audio file `file_name`
        Features supported:
            - MFCC (mfcc)
            - Chroma (chroma)
            - MEL Spectrogram Frequency (mel)
            - Contrast (contrast)
            - Tonnetz (tonnetz)
        e.g:
        `features = extract_feature()`
        """
        X = audio_signal
        sample_rate = sample_rate
        n_fft_ms=kwargs.get("n_fft_ms")
        n_fft = pow(2, math.ceil(math.log2(n_fft_ms*sample_rate)))
        # A win_length<= n_fft.
        extract_all_cepstral=kwargs.get("extract_all_cepstral")  
        mfcc = kwargs.get("mfcc")
        chroma_stft = kwargs.get("chroma_stft")
        chroma_cens = kwargs.get("chroma_cens")
        mel = kwargs.get("mel")
        contrast = kwargs.get("contrast")
        tonnetz = kwargs.get("tonnetz")
        spec_cent = kwargs.get("spec_cent")
        spec_bw = kwargs.get("spec_bw")
        rolloff = kwargs.get("rolloff")
        zcr = kwargs.get("zcr")
        rms = kwargs.get("rms")
    
        header = np.array([])
        result = np.array([])
      
        if chroma_stft['extract'] or contrast['extract'] or extract_all_cepstral:
            stft = np.abs(librosa.stft(X, n_fft=n_fft))**2

        if mfcc['extract'] or extract_all_cepstral :
            n_mfcc= mfcc['n_mfcc']
            mfccs_h = ["{}_{}".format(mfcc ['header'], i) for i in range(1, n_mfcc+1)]
            mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_fft=n_fft, n_mfcc=n_mfcc).T, axis=0).flatten()
            result = np.hstack((result, mfccs))
            header = np.hstack((header, mfccs_h))    
            
            if mfcc['mfcc_delta']['extract'] or extract_all_cepstral:
                mfccs_delta_h=["{}_{}".format(mfcc['mfcc_delta']['header'], i) for i in range(1, n_mfcc+1)]
                mfccs_delta = librosa.feature.delta(mfccs)
                result = np.hstack((result, mfccs_delta))
                header = np.hstack((header, mfccs_delta_h)) 

            if mfcc['mfcc_delta2']['extract'] or extract_all_cepstral:
                mfccs_delta2_h=["{}_{}".format(mfcc['mfcc_delta2']['header'], i) for i in range(1, n_mfcc+1)]
                mfccs_delta2 = librosa.feature.delta(mfccs,  order=2)
                result = np.hstack((result, mfccs_delta2))
                header = np.hstack((header, mfccs_delta2_h))  

        if chroma_stft['extract'] or extract_all_cepstral:
            chroma_stft_r = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T, axis=0).flatten()
            if (chroma_stft['chroma_12']):
                chroma_stft_h = chroma_stft['header']
                result = np.hstack((result, chroma_stft_r))
                header = np.hstack((header, chroma_stft_h))

            if chroma_stft['chroma_mean']['extract'] or extract_all_cepstral:
                chroma_mean_h = chroma_stft['chroma_mean']['header']
                chroma_mean = np.mean( chroma_stft_r)
                result = np.hstack((result, chroma_mean))
                header = np.hstack((header, chroma_mean_h)) 

            if (chroma_stft['chroma_std']['extract']) or extract_all_cepstral:
                chroma_std_h = chroma_stft['chroma_std']['header']
                chroma_std = np.std(chroma_stft_r)
                result = np.hstack((result, chroma_std))
                header = np.hstack((header, chroma_std_h))     
               
        if chroma_cens['extract'] or extract_all_cepstral:
            chroma_cens_h = chroma_cens['header']
            chroma_cens = np.mean(librosa.feature.chroma_cens(y=X, sr=sample_rate).T, axis=0).flatten()
            result = np.hstack((result, chroma_cens))
            header = np.hstack((header, chroma_cens_h)) 
        
        
        if mel['extract'] or extract_all_cepstral:
            mel_h = mel['header']
            mel = np.mean(librosa.feature.melspectrogram(y=X, sr=sample_rate, n_fft=n_fft, hop_length=25).T, axis=0).flatten()
            mel_mean = np.mean(mel)
            result = np.hstack((result, mel_mean))
            header = np.hstack((header, mel_h)) 
    
        if contrast['extract'] or extract_all_cepstral:
            n_bands= contrast['n_bands']
            contrast_h = ["{}_{}".format(contrast['header'], i) for i in range(0, n_bands+1)]
            contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate,n_bands=n_bands).T,axis=0).flatten()
            result = np.hstack((result, contrast))
            header = np.hstack((header, contrast_h))
     
        if tonnetz['extract'] or extract_all_cepstral:
            tonnetz_h = ["{}_{}".format(tonnetz['header'], i) for i in range(0, 6)]
            #tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(X), sr=sample_rate).T,axis=0)
            y_t = librosa.effects.harmonic(X)
            tonnetz = np.mean(librosa.feature.tonnetz(y=y_t, sr=sample_rate).T,axis=0)
            result = np.hstack((result, tonnetz))
            header = np.hstack((header, tonnetz_h)) 

    
        # Spectral centroid from time-series input:        
        if spec_cent['extract'] or extract_all_cepstral:
            spec_cent_h = spec_cent['header']
            spec_cent = np.mean(librosa.feature.spectral_centroid(y=X, sr=sample_rate, n_fft=n_fft).T,axis=0).flatten()
            result = np.hstack((result, spec_cent))
            header = np.hstack((header, spec_cent_h))    
    
        # Spectral bandwidth from time-series input:  
        if spec_bw['extract'] or extract_all_cepstral:
            spec_bw_h = spec_bw['header']
            spec_bw = np.mean (librosa.feature.spectral_bandwidth(y=X, sr=sample_rate, n_fft=n_fft).T, axis=0).flatten()
            result = np.hstack((result, spec_bw))
            header = np.hstack((header, spec_bw_h))   

        if rolloff['extract'] or extract_all_cepstral:
            rolloff_h = rolloff['header']
            rolloff = np.mean(librosa.feature.spectral_rolloff(y=X, sr=sample_rate, n_fft=n_fft).T, axis=0).flatten()
            result = np.hstack((result, rolloff))
            header = np.hstack((header, rolloff_h)) 
        
        if zcr['extract']:
            zcr_h = zcr['header']
            zcr = np.mean(librosa.feature.zero_crossing_rate(X))
            result = np.hstack((result, zcr))
            header = np.hstack((header, zcr_h)) 

        if rms['extract'] or extract_all_cepstral:
            rms_h = rms['header']
            rms = np.mean(librosa.feature.rms(y=X))
            result = np.hstack((result, rms))
            header = np.hstack((header, rms_h)) 
            
            
        Frame = pd.DataFrame([result], columns = [header])
        
    
        return Frame

    # 6. Load Data
    def get_features(self, audio_file):
        audio_features = cepstral_features | prosodic_features
        audio_features['mfcc']['n_mfcc'] =  self.n_mfcc
        audio_features['n_fft'] =  self.n_fft
        frame_size= audio_features ['frame_size']
        hop_length = audio_features ['frame_slice']
        framing = audio_features['framing']
        
            
        # Load audio Signal
        audio_signal_raw, sample_rate = librosa.load(audio_file, sr=None)
        
        # Frame audio signal
        audio_signal_frm  = self.frameW_audio_signal(audio_signal_raw, sample_rate = sample_rate, frame_size=frame_size,  hop_length=hop_length, framing = framing)
        
        audio_feature = self.extract_feature_ours(audio_signal_frm, sample_rate, **audio_features)
            
        return audio_feature
        
    
        