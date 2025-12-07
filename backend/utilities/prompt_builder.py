"""
Prompt Builder - Centralized prompts for Claude API
"""

class PromptBuilder:
    """Build prompts for Claude API calls."""
    
    @staticmethod
    def ocr_extraction(num_images: int) -> str:
        """Prompt for extracting medication info from images."""
        if num_images == 1:
            return """Extract from this medication packaging:
- Brand name (e.g., "Advil", "Tylenol")
- Dosage strength (e.g., "100mg", "40mg/ml")
- Dosage form (e.g., "tablet", "suspension", "liquid")
- Route (e.g., "oral", "topical")

Return only the extracted information. Correct any OCR errors. 
Do NOT include warnings, directions, or usage instructions."""
        
        return f"""Viewing {num_images} images of the same medication packaging.

Extract and combine information from ALL images:
- Brand name (e.g., "Advil", "Tylenol")
- Active ingredient (e.g., "ibuprofen", "acetaminophen")
- Dosage strength (e.g., "100mg", "40mg/ml")
- Dosage form (e.g., "tablet", "suspension", "liquid")
- Route (e.g., "oral", "topical")

Combine information from all images. Correct OCR errors.
Do NOT include warnings, directions, or usage instructions."""
    
    @staticmethod
    def fda_label_cleaning(raw_data: dict) -> str:
        """Prompt for cleaning and structuring FDA label data."""
        return f"""Clean this raw FDA drug label data into structured JSON.

Raw data:
{raw_data}

Return ONLY valid JSON in this exact format:
{{
    "purpose": "[What condition/symptom this drug treats - e.g., 'Fever reducer and pain reliever' NOT just the drug name]",
    "dosage_instructions": "[General usage instructions as a clean paragraph]",
    "dosing_chart": [
        {{
            "min_weight_lb": numeric or null,
            "max_weight_lb": numeric or null,
            "min_age_months": numeric or null,
            "max_age_months": numeric or null,
            "dose_ml": numeric or null,
            "dose_text": "text or null"
        }}
    ],
    "warnings": "[All warnings and precautions as clean paragraph]",
    "contraindications": "[When NOT to use this drug as clean paragraph]",
    "adverse_reactions": "[Possible side effects as clean paragraph]"
}}

CRITICAL RULES FOR ALL TEXT FIELDS:
1. Remove ALL formatting symbols: bullets (•, -, *), asterisks, arrows, special characters
2. Remove excessive whitespace, line breaks, and tabs
3. Make text flow naturally as readable paragraphs
4. Remove instructional phrases like:
   - "see chart below"
   - "check the dose chart below"
   - "find right dose on chart below"
   - "refer to dosing table"
   - "consult the chart"
5. If a field is truly empty or missing, use empty string ""
6. For "purpose": Extract what condition/symptom the drug treats, NOT just the active ingredient name

DOSING CHART RULES (CRITICAL):
- ONLY extract if there is an actual weight/age/dose TABLE in the text
- If NO table exists, return empty array []
- Return array of objects, one per row in the table
- ALWAYS CONVERT AGES TO MONTHS:
  * "6-11 mos" → min_age_months: 6, max_age_months: 11
  * "12-23 mos" → min_age_months: 12, max_age_months: 23
  * "2 yr" → min_age_months: 24, max_age_months: 35
  * "2-3 yr" → min_age_months: 24, max_age_months: 47
  * "4-5 yr" → min_age_months: 48, max_age_months: 71
  * "under 2 yr" → min_age_months: null, max_age_months: 23
  * "under 6 months" → min_age_months: null, max_age_months: 5
  * "11 yr" → min_age_months: 132, max_age_months: 143
  
- Weight stays in pounds (lb):
  * "12-17 lb" → min_weight_lb: 12, max_weight_lb: 17
  * "18-23 lb" → min_weight_lb: 18, max_weight_lb: 23
  * "under 24 lb" → min_weight_lb: null, max_weight_lb: 23
  
- For numeric doses (e.g., "1.25 mL"):
  * Use dose_ml field with number only: dose_ml: 1.25
  * Set dose_text to null
  
- For text instructions (e.g., "ask a doctor"):
  * Use dose_text field: dose_text: "ask a doctor"
  * Set dose_ml to null

EXAMPLES OF GOOD PURPOSE EXTRACTION:
✓ "Fever reducer and pain reliever"
✓ "Temporarily relieves nasal congestion and runny nose"
✓ "Antihistamine for relief of allergy symptoms"
✗ "Ibuprofen" (This is the ingredient, not the purpose!)
✗ "Acetaminophen oral suspension" (This is the product name, not the purpose!)

Return ONLY the JSON object. No markdown code blocks, no explanations, no preamble."""