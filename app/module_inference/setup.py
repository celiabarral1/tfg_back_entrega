from setuptools import setup
setup(     
    name='inference',
    author='Paula Fernández Suárez',
    author_email='paulafernandezsuarez03@gmail.com',
    url='https://www.linkedin.com/in/paulafernandezsuarez/',
    license='MIT',
    version='1.0',
    packages=['infere_emotion', 'models', 'utils', 'features_extraction'],
    install_requires=[
        'pandas==1.5.3',
        'numpy==1.23.5',
        'matplotlib>=3.6.0',
        'librosa>=0.9.2',
        'scikit-learn==1.2.1',
        'xgboost>=1.7.5',
        'catboost>=1.1.0',
        'pydub>=0.25.1',
        'audeer>= 2.1.2',
        'audinterface>= 1.2.2',
        'transformers>=4.41.2',
        'torch>=2.0.0',
        'audonnx == 0.6.0',
        'paho-mqtt',
        'onnx'
    ]
)