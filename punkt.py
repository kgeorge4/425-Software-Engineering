import spacy

def download_and_load_model(model_name='en_core_web_md'):
    # Check if the model is installed
    try:
        nlp = spacy.load(model_name)
        print(f"Model '{model_name}' loaded successfully.")
    except OSError:
        print(f"Model '{model_name}' not found. Downloading the model...")
        spacy.cli.download(model_name)
        nlp = spacy.load(model_name)
        print(f"Model '{model_name}' downloaded and loaded successfully.")
    return nlp



download_and_load_model()
