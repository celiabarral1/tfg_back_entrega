prosodic_features = {
				
    "Energy": {
        "extract": False,
        "header": "F0"
    },
    "F0": {
        "extract": False,
        "header": "F0"
    },
    "zcr": {
        "extract": True,
        "header": "zcr"
    }
}
	
cepstral_features = {
    "framing": False,
    "frame_size": 0.032,  
    "frame_slice": 0.01,
    "default_sample_rate": 16000,
	"n_fft_ms": 0.023,
    
    "mfcc": {
        "extract": True,
        "header": "mfcc",
        "mfcc_delta": {
                        "extract": True,
                        "header": "mfcc_delta"
                    },
        "mfcc_delta2": {
                        "extract": True,
                        "header": "mfcc_delta2"
                    }
    },
    
    "chroma_stft": {
        "extract": True,
        "chroma_12": True,
        "header": ["Chroma_C","Chroma_C#","Chroma_D","Chroma_D#","Chroma_E","Chroma_F","Chroma_F#","Chroma_G","Chroma_G#","Chroma_A","Chroma_A#","Chroma_B"],
        "chroma_mean": {
                        "extract": True,
                        "header": "chroma_mean"
                        },
        "chroma_std": {
                        "extract": True,
                        "header": "chroma_std"
                    }
    },	

    "chroma_cens": {
        "extract": False,
        "header": ["Cens_C","Cens_C#","Cens_D","Cens_D#","Cens_E","Cens_F","Cens_F#","Cens_G","Cens_G#","Cens_A","Cens_A#","Cens_B"]
    },

    "mel": {
        "extract": False,
        "header": "mel"
    },
    "contrast": {
        "extract": True,
        "n_bands": 6,
        "header": "spectral_contrast"
    }
    ,
    "tonnetz": {
        "extract": False,
        "n_dimentions": 6,
        "header": "tc_tonnetz"
    },
    "spec_cent": {
        "extract": True,
        "header": "spectral_centroid"
    },
    "spec_bw": {
        "extract": True,
        "header": "spectral_bandwidth"
    },
    "rolloff": {
        "extract": True,
        "header": "rolloff"
    },
    "rms": {
        "extract": True,
        "header": "rmsa"
    }
}