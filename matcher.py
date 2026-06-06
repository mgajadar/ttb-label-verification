import re
from thefuzz import fuzz

class LabelMatcher:
    def __init__(self, expected: dict, extracted: dict):
        self.expected = expected
        self.extracted = extracted

    def verify_brand_name(self):
        exp = str(self.expected.get("brand_name", "")).upper()
        ext = str(self.extracted.get("brand_name", "")).upper()
        
        score = fuzz.ratio(exp, ext)
        if score >= 85:
            return {"passed": True, "message": f"Match ({score}% similarity)"}
        return {"passed": False, "message": f"Failed: Expected '{exp}', found '{ext}'"}

    def verify_class_type(self):
        exp = str(self.expected.get("class_type", "")).upper()
        ext = str(self.extracted.get("class_type", "")).upper()
        
        score = fuzz.token_sort_ratio(exp, ext)
        if score >= 80:
            return {"passed": True, "message": f"Match ({score}% similarity)"}
        return {"passed": False, "message": f"Failed: Expected '{exp}', found '{ext}'"}

    def verify_abv(self):
        exp = str(self.expected.get("abv", ""))
        ext = str(self.extracted.get("abv", ""))

        exp_match = re.search(r"\d+(\.\d+)?", exp)
        ext_match = re.search(r"\d+(\.\d+)?", ext)

        if exp_match and ext_match:
            exp_val = float(exp_match.group())
            ext_val = float(ext_match.group())
            if exp_val == ext_val:
                return {"passed": True, "message": f"Verified {exp_val}%"}
        return {"passed": False, "message": f"Failed: Expected '{exp}', found '{ext}'"}

    def verify_net_contents(self):
        exp = str(self.expected.get("net_contents", "")).upper()
        ext = str(self.extracted.get("net_contents", "")).upper()
        
        score = fuzz.partial_ratio(exp, ext)
        if score >= 80:
             return {"passed": True, "message": f"Match ({score}% similarity)"}
        return {"passed": False, "message": f"Failed: Expected '{exp}', found '{ext}'"}

    def verify_government_warning(self):
        ext = str(self.extracted.get("government_warning", ""))
        
        if ext.startswith("GOVERNMENT WARNING:"):
            return {"passed": True, "message": "Exact header and text verified."}
        return {"passed": False, "message": "Failed: Missing mandatory 'GOVERNMENT WARNING:' in all-caps."}

    def run_compliance_check(self):
        details = {
            "brand_name": self.verify_brand_name(),
            "class_type": self.verify_class_type(), 
            "abv": self.verify_abv(),
            "net_contents": self.verify_net_contents(),
            "government_warning": self.verify_government_warning()
        }

        is_approved = all(field["passed"] for field in details.values())

        return {
            "is_approved": is_approved,
            "details": details
        }