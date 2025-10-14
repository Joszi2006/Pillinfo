"""
Train Custom MedSpacy NER Model
Run this AFTER collecting training data with build_training_data.py

Usage:
    python backend/models/train_medspacy.py
"""

import spacy
from spacy.training import Example
import json
from pathlib import Path
import random

def load_training_data(data_path: str):
    """
    Load training data from JSON file.
    
    Expected format:
    [
        {
            "text": "Take Lipitor 20mg orally",
            "entities": [[5, 12, "DRUG"], [13, 17, "DOSAGE"], [18, 24, "ROUTE"]]
        }
    ]
    """
    with open(data_path, 'r') as f:
        return json.load(f)

def train_custom_ner(
    training_data_path: str = "data/training_data/ner_annotations.json",
    output_path: str = "backend/models/custom_ner/model_v1",
    n_iter: int = 30,
    drop_rate: float = 0.5
):
    """
    Train a custom NER model with MedSpacy.
    
    Args:
        training_data_path: Path to training data JSON
        output_path: Where to save the trained model
        n_iter: Number of training iterations
        drop_rate: Dropout rate (prevents overfitting)
    """
    
    print("=" * 60)
    print("🎓 TRAINING CUSTOM MEDSPACY NER MODEL")
    print("=" * 60)
    
    # Step 1: Load training data
    print("\n📂 Loading training data...")
    try:
        train_data = load_training_data(training_data_path)
        print(f" Loaded {len(train_data)} training examples")
    except FileNotFoundError:
        print(f" Training data not found at: {training_data_path}")
        print("Run build_training_data.py first to create training data!")
        return
    except json.JSONDecodeError:
        print(f" Invalid JSON in training data file")
        return
    
    if len(train_data) < 10:
        print(f"⚠️  Warning: Only {len(train_data)} examples. Need at least 50 for good accuracy.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Step 2: Load base spaCy model
    print("\n📦 Loading base spaCy model...")
    try:
        nlp = spacy.load("en_core_web_sm")
        print("Base model loaded")
    except OSError:
        print("Base model not found. Installing...")
        import os
        os.system("python -m spacy download en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    
    # Step 3: Setup NER pipeline
    print("\n🔧 Setting up NER pipeline...")
    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner", last=True)
    else:
        ner = nlp.get_pipe("ner")
    
    # Add labels
    labels = ["DRUG", "DOSAGE", "ROUTE", "FORM"]
    for label in labels:
        ner.add_label(label)
    print(f" Added labels: {', '.join(labels)}")
    
    # Step 4: Convert training data to spaCy format
    print("\n📝 Preparing training examples...")
    train_examples = []
    for item in train_data:
        doc = nlp.make_doc(item["text"])
        
        # Convert entity list to dict format
        entities = []
        for start, end, label in item["entities"]:
            entities.append((start, end, label))
        
        example = Example.from_dict(doc, {"entities": entities})
        train_examples.append(example)
    
    print(f"Prepared {len(train_examples)} training examples")
    
    # Step 5: Train the model
    print(f"\n🏋️ Training for {n_iter} iterations...")
    print("This may take a few minutes...\n")
    
    # Disable other pipes during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.create_optimizer()
        
        for iteration in range(n_iter):
            random.shuffle(train_examples)
            losses = {}
            
            # Batch training
            for batch in spacy.util.minibatch(train_examples, size=8):
                nlp.update(batch, drop=drop_rate, losses=losses, sgd=optimizer)
            
            # Print progress every 5 iterations
            if (iteration + 1) % 5 == 0:
                print(f"Iteration {iteration + 1}/{n_iter} - Loss: {losses.get('ner', 0):.2f}")
    
    print("\n Training complete!")
    
    # Step 6: Save the model
    print(f"\n💾 Saving model to {output_path}...")
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    nlp.to_disk(output_dir)
    print("Model saved!")
    
    # Step 7: Test the model
    print("\n Testing trained model...")
    test_texts = [
        "Take Lipitor 20mg orally once daily",
        "Advil 200mg tablet by mouth as needed",
        "Metformin 500mg oral twice daily"
    ]
    
    for test_text in test_texts:
        doc = nlp(test_text)
        print(f"\nText: '{test_text}'")
        if doc.ents:
            for ent in doc.ents:
                print(f"  - {ent.text} ({ent.label_})")
        else:
            print("  - No entities found")
    
    # Step 8: Instructions for using the model
    print("\n" + "=" * 60)
    print("🎉 MODEL TRAINING COMPLETE!")
    print("=" * 60)
    print("\nTo use your trained model:")
    print("1. Update your .env file:")
    print(f"   MEDSPACY_MODEL=\"{output_path}\"")
    print("\n2. Restart your server:")
    print("   python backend/main.py")
    print("\n3. Your system will now use the custom trained model!")
    print("=" * 60)

if __name__ == "__main__":
    # Train the model
    train_custom_ner(
        training_data_path="data/training_data/ner_annotations.json",
        output_path="backend/models/custom_ner/model_v1",
        n_iter=30
    )