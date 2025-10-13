"""
Active Learning System - Learn from Successful Extractions
This automatically improves the model over time!
"""

# backend/models/build_training_data.py

import json
from datetime import datetime
from pathlib import Path
from collections import Counter

class TrainingDataBuilder:
    """
    Builds training data from successful extractions.
    This is SMART - learns from real usage!
    """
    
    def __init__(
        self,
        success_log="data/training_data/successful_extractions.log",
        output_path="data/training_data/ner_annotations.json"
    ):
        self.success_log = success_log
        self.output_path = output_path
    
    def convert_logs_to_training_data(self, min_examples=10):
        """
        Convert successful extraction logs to NER training format.
        
        Args:
            min_examples: Minimum successful extractions before creating training data
        
        Returns:
            Number of training examples created
        """
        if not Path(self.success_log).exists():
            print(f"⚠️  No successful extractions log found at {self.success_log}")
            print("System will create this automatically as users interact with it.")
            return 0
        
        training_examples = []
        stats = {
            "total_logs": 0,
            "successful": 0,
            "with_drug": 0,
            "with_dosage": 0,
            "with_route": 0
        }
        
        print("Reading successful extractions...")
        with open(self.success_log) as f:
            for line in f:
                if not line.strip():
                    continue
                
                stats["total_logs"] += 1
                entry = json.loads(line)
                
                # Only use confirmed successful extractions
                if not entry.get("success") or not entry.get("confirmed_drug"):
                    continue
                
                stats["successful"] += 1
                
                # Build NER example
                ner_example = self._build_ner_example(entry)
                
                if ner_example["entities"]:
                    training_examples.append(ner_example)
                    
                    # Update stats
                    for ent in ner_example["entities"]:
                        if ent[2] == "DRUG":
                            stats["with_drug"] += 1
                        elif ent[2] == "DOSAGE":
                            stats["with_dosage"] += 1
                        elif ent[2] == "ROUTE":
                            stats["with_route"] += 1
        
        # Check if we have enough data
        if len(training_examples) < min_examples:
            print(f"⚠️  Only {len(training_examples)} examples found.")
            print(f"Need at least {min_examples} to train effectively.")
            print("Keep using the system to collect more data!")
            return 0
        
        # Save training data
        Path(self.output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(training_examples, f, indent=2)
        
        # Print stats
        print("\n" + "="*60)
        print("✅ Training Data Built from Real Usage!")
        print("="*60)
        print(f"Total logs processed:     {stats['total_logs']}")
        print(f"Successful extractions:   {stats['successful']}")
        print(f"Training examples created: {len(training_examples)}")
        print(f"  - With drug names:      {stats['with_drug']}")
        print(f"  - With dosages:         {stats['with_dosage']}")
        print(f"  - With routes:          {stats['with_route']}")
        print(f"\nSaved to: {self.output_path}")
        print("="*60)
        
        return len(training_examples)
    
    def _build_ner_example(self, entry):
        """Build NER example from log entry."""
        text = entry["text"]
        ner_example = {
            "text": text,
            "entities": []
        }
        
        # Find drug position
        confirmed_drug = entry.get("confirmed_drug", "")
        if confirmed_drug:
            drug_start = text.lower().find(confirmed_drug.lower())
            if drug_start != -1:
                ner_example["entities"].append([
                    drug_start,
                    drug_start + len(confirmed_drug),
                    "DRUG"
                ])
        
        # Find dosage positions
        for dosage in entry.get("dosages", []):
            dos_start = text.find(dosage)
            if dos_start != -1:
                ner_example["entities"].append([
                    dos_start,
                    dos_start + len(dosage),
                    "DOSAGE"
                ])
        
        # Find route positions
        for route in entry.get("routes", []):
            route_start = text.lower().find(route.lower())
            if route_start != -1:
                ner_example["entities"].append([
                    route_start,
                    route_start + len(route),
                    "ROUTE"
                ])
        
        # Find form positions
        for form in entry.get("forms", []):
            form_start = text.lower().find(form.lower())
            if form_start != -1:
                ner_example["entities"].append([
                    form_start,
                    form_start + len(form),
                    "FORM"
                ])
        
        return ner_example
    
    def analyze_extraction_quality(self):
        """
        Analyze the quality of extractions.
        Helps decide when to retrain.
        """
        if not Path(self.success_log).exists():
            print("No data to analyze yet.")
            return
        
        success_count = 0
        failure_count = 0
        drug_types = Counter()
        
        with open(self.success_log) as f:
            for line in f:
                if not line.strip():
                    continue
                
                entry = json.loads(line)
                
                if entry.get("success"):
                    success_count += 1
                    drug_types[entry.get("confirmed_drug", "Unknown")] += 1
                else:
                    failure_count += 1
        
        total = success_count + failure_count
        if total == 0:
            print("No extractions logged yet.")
            return
        
        success_rate = (success_count / total) * 100
        
        print("\n" + "="*60)
        print("📊 Extraction Quality Analysis")
        print("="*60)
        print(f"Total extractions:  {total}")
        print(f"Successful:         {success_count} ({success_rate:.1f}%)")
        print(f"Failed:             {failure_count} ({100-success_rate:.1f}%)")
        print(f"\nTop 10 drugs extracted:")
        for drug, count in drug_types.most_common(10):
            print(f"  {drug}: {count}x")
        print("="*60)
        
        # Recommendation
        if success_count >= 50:
            print("\n✅ You have enough data to train a custom model!")
            print("   Run: python backend/models/train_medspacy.py")
        elif success_count >= 20:
            print("\n⚠️  Getting close! Collect a few more examples.")
        else:
            print(f"\n📈 Keep using the system. Need {50 - success_count} more successful extractions.")


# Main execution
if __name__ == "__main__":
    builder = TrainingDataBuilder()
    
    print("="*60)
    print("Active Learning - Training Data Builder")
    print("="*60)
    
    # Analyze current data quality
    print("\nStep 1: Analyzing extraction quality...")
    builder.analyze_extraction_quality()
    
    # Build training data
    print("\nStep 2: Building training data from successful extractions...")
    num_examples = builder.convert_logs_to_training_data(min_examples=10)
    
    if num_examples > 0:
        print("\n✅ Ready to train! Next steps:")
        print("   1. python backend/models/train_medspacy.py")
        print("   2. Update .env: MEDSPACY_MODEL=backend/models/custom_ner/model_v2")
        print("   3. Restart server")
    else:
        print("\n📈 Not enough data yet. Keep using the system!")