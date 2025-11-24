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
            {{Brand name, Dosage strength, Dosage route and form }}

            Return only relevant text. Correct OCR errors. No warnings or directions."""
        
        return f"""Viewing {num_images} images of same medication packaging.
            Extract across ALL images:
            - Brand name
            - Active ingredient  
            - Dosage form
            - Route

            Combine information from all images. Correct OCR errors. No warnings or directions."""
                
    @staticmethod
    def fda_label_cleaning(raw_data: dict) -> str:
        """Prompt for cleaning and structuring FDA label data."""
        return f"""Clean this raw FDA drug label data into structured JSON.
            Raw data:
            {raw_data}

            Return ONLY valid JSON in this exact format:
            {{
                "purpose": "[Clean, readable paragraph describing what this drug treats or prevents]",
                "dosage_instructions": "[Clean, readable paragraph with general usage instructions]",
                "dosing_chart": [
                    {{
                        "min_weight_lb": numeric value of leftmost weight bound or null,
                        "max_weight_lb": numeric value of rightmost weight bound or null,
                        "min_age_months": numeric value of leftmost age bound in MONTHS or null,
                        "max_age_months": numeric value of rightmost age bound in MONTHS or null,
                        "dose_ml": numeric dose value or null,
                        "dose_text": "text like 'ask a doctor' or null"
                    }}
                ],
                "warnings": "Clean, readable paragraph with all warnings and precautions",
                "contraindications": "Clean, readable paragraph with contraindications",
                "adverse_reactions": "Clean, readable paragraph with side effects and adverse reactions"
            }}

            CRITICAL RULES:

            For ALL text fields:
            - Remove bullet points, asterisks, formatting symbols
            - Remove excessive whitespace and line breaks
            - Make text flow naturally as readable paragraphs
            - If field is empty or missing, use empty string ""

            For dosing_chart (VERY IMPORTANT):
            - ONLY extract if there is an actual weight/age/dose table in the text
            - If NO table exists, return empty array []
            - Return array of objects, one object per row in the dosing table
            - CONVERT ALL AGES TO MONTHS (this is critical):
            * "6-11 mos" becomes min_age_months: 6, max_age_months: 11
            * "12-23 mos" becomes min_age_months: 12, max_age_months: 23
            * "2 yr" becomes min_age_months: 24, max_age_months: 24
            * "2-3 yr" becomes min_age_months: 24, max_age_months: 47 (3 years = 36 months, but end of 3rd year is 47)
            * "4-5 yr" becomes min_age_months: 48, max_age_months: 71
            * "under 2 yr" becomes min_age_months: null, max_age_months: 23
            * "11 yr" becomes min_age_months: 132, max_age_months: 143
            - Weight stays in pounds (lb):
            * "12-17 lb" becomes min_weight_lb: 12, max_weight_lb: 17
            * "under 24 lb" becomes min_weight_lb: null, max_weight_lb: 23
            - For numeric doses: use dose_ml field (as number), set dose_text to null
            - For "ask a doctor": use dose_text field (as string), set dose_ml to null

            Return ONLY the JSON object, no markdown code blocks, no explanations, no extra text."""