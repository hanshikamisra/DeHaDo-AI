# utils.py

import re

def clean_field(field, value):
    """
    Cleans the extracted value based on the field type.
    """
    value = value.strip(' \"\\n\\t,')
    if field in ["candidate_name", "father_husband_name", "qualification", "marital_status", "gender", "nationality"]:
        value = re.sub(r'[^\w\s\-]', '', value)
    elif field in ["contact_number", "alternate_number", "aadhaar_card"]:
        value = re.sub(r"[^\d]", "", value)
    elif field == "languages_known":
        value = re.sub(r'[^a-zA-Z, ]', '', value)
    elif field == "experience":
        value = re.sub(r'[^a-zA-Z0-9, \-]', '', value)
    elif field == "references":
        value = re.sub(r'[^a-zA-Z0-9,\- ]', '', value)
    return value

FIELD_PATTERNS = {
    "candidate_name": r"(?:candidate_name|candidatename)[^a-zA-Z0-9]*[:=]?\s*([^\n,]+)",
    "father_husband_name": r"(?:father_husband_name|fathername|husbandname)[^a-zA-Z0-9]*[:=]?\s*([^\n,]+)",
    "date_of_birth": r"(?:date_of_birth|dob)[^a-zA-Z0-9]*[:=]?\s*([0-9/\-]+)",
    "qualification": r"(?:qualification)[^a-zA-Z0-9]*[:=]?\s*([^\n,]+)",
    "marital_status": r"(?:marital_status)[^a-zA-Z0-9]*[:=]?\s*([^\n,]+)",
    "gender": r"(?:gender)[^a-zA-Z0-9]*[:=]?\s*([^\n,]+)",
    "nationality": r"(?:nationality)[^a-zA-Z0-9]*[:=]?\s*([^\n,]+)",
    "blood_group": r"(?:blood_group)[^a-zA-Z0-9]*[:=]?\s*([A-O+-]+)",
    "present_address": r"(?:present_address)[^a-zA-Z0-9]*[:=]?\s*(.+?)(?=\s*(permanent_address|alternate_number|contact_number|languages_known|place|$))",
    "permanent_address": r"(?:permanent_address)[^a-zA-Z0-9]*[:=]?\s*(.+?)(?=\s*(alternate_number|contact_number|languages_known|place|$))",
    "contact_number": r"(?:contact_number)[^a-zA-Z0-9]*[:=]?\s*(\d{10,})",
    "alternate_number": r"(?:alternate_number)[^a-zA-Z0-9]*[:=]?\s*(\d{10,})",

    "languages_known": r"(?:languages_known)[^a-zA-Z0-9]*[:=]?\s*([^\n]+?)(?=\s*(place|date|experience|$))",

    "place": r"(?:place)[^a-zA-Z0-9]*[:=]?\s*([a-zA-Z ]+)",
    "date": r"(?:date)[^a-zA-Z0-9]*[:=]?\s*([0-9/\-]+)",
    "experience": r"(?:experience)[^a-zA-Z0-9]*[:=]?\s*(.+?)(?=\s*(references|aadhaar_card|pan_card|$))",
    "references": r"(?:references)[^a-zA-Z0-9]*[:=]?\s*(.+?)(?=\s*(aadhaar_card|pan_card|$))",

    "aadhaar_card": r"(?:aadhaar_card|aadhaar)[^a-zA-Z0-9]*[:=]?\s*(\d[\d ]{10,})",

    "pan_card": r"(?:pan_card|pancard)[^a-zA-Z0-9]*[:=]?\s*([A-Z]{5}[0-9]{4}[A-Z])"
}

def clean_field(field, value):
    value = value.strip(' "\n\t,')
    if field in ["candidate_name", "father_husband_name", "qualification", "marital_status", "gender", "nationality"]:
        value = re.sub(r'[^\w\s\-]', '', value)
    elif field in ["contact_number", "alternate_number", "aadhaar_card"]:
        value = re.sub(r"[^\d]", "", value)
    elif field == "languages_known":
        value = re.sub(r'[^a-zA-Z, ]', '', value)
    elif field == "experience":
        value = re.sub(r'[^a-zA-Z0-9, \-]', '', value)
    elif field == "references":
        value = re.sub(r'[^a-zA-Z0-9,\- ]', '', value)
    return value


def extract_fields_from_raw(raw_output: str) -> dict:
    # Step 0: Pre-clean to reduce noise
    raw_output = raw_output.replace('\n', ' ').replace('\r', '')
    raw_output = raw_output.replace('“', '"').replace('”', '"')
    raw_output = re.sub(r'\s+', ' ', raw_output)
    raw_output = raw_output.replace("\\", "")
    
    result = {}
    for field, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, raw_output, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).strip()
            value = clean_field(field, value)
            result[field] = value
    return result


FIELD_NAME_MAPPING = {
    "candidate_name": "candidatename",
    "father_husband_name": "Father/husbandname",
    "date_of_birth": "Dateofbirth",
    "qualification": "qualification",
    "marital_status": "maritalstatus",
    "gender": "gender",
    "nationality": "nationality",
    "blood_group": "bloodgroup",
    "present_address": "presentaddress",
    "permanent_address": "permanentaddress",
    "contact_number": "contactnumber",
    "alternate_number": "AlternateNo",
    "languages_known": "languageknown",
    "place": "place",
    "date": "date",
    "experience": "experience",
    "references": "referencescmob1",
    "aadhaar_card": "aadhaarcard",
    "pan_card": "pancard",
    "experience1": "experience1",
    "referencescmob2": "referencescmob2"
}

def convert_flat_to_structured(flat_output: dict) -> list:
    structured = {}

    for internal_key, display_key in FIELD_NAME_MAPPING.items():
        if internal_key in flat_output:
            try:
                cleaned_value = clean_field(internal_key, flat_output[internal_key])
            except:

                cleaned_value = flat_output[internal_key]
            structured[display_key]=cleaned_value

    return structured
