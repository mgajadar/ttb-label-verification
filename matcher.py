import re
from thefuzz import fuzz

class LabelMatcher:
    def __init__(self, expected: dict, extracted: dict):
        """
        Initializes the matching engine.
        :param expected: Dictionary of inputs from the UI (COLA Application Data)
        :param extracted: Dictionary or Pydantic object from the Vision Model
        """
        self.expected = {k.lower(): str(v).strip() for k, v in expected.items()}
        self.extracted = {k.lower(): str(v).strip() for k, v in extracted.items()}

    def verify_brand_name(self, threshold: int = 85) -> tuple[bool, str]:
        """Applies fuzzy matching to handle natural text/casing nuances."""
        exp = self.expected.get("brand_name", "")
        ext = self.extracted.get("brand_name", "")
        
        if not exp or not ext:
            return False, "Missing data"
            
        ratio = fuzz.ratio(exp.lower(), ext.lower())
        if ratio >= threshold:
            return True, f"Match ({ratio}% match similarity)"
        return False, f"Mismatch: Expected '{exp}', Found '{ext}'"

    def verify_abv(self) -> tuple[bool, str]:
        """Normalizes and extracts numerical values to evaluate alcohol content consistently."""
        exp = self.expected.get("abv", "")
        ext = self.extracted.get("abv", "")
        
        #regex for numbers and %
        exp_digits = "".join(re.findall(r'\d+', exp))
        ext_digits = "".join(re.findall(r'\d+', ext))
        
        if exp_digits and ext_digits and exp_digits == ext_digits:
            return True, f"Match: Verified {ext}"
        return False, f"Mismatch: Expected '{exp}', Found '{ext}'"

    def verify_net_contents(self, threshold: int = 90) -> tuple[bool, str]:
        """Fuzzy matches fluid content descriptions (e.g., '750 mL' vs '750ml')."""
        exp = self.expected.get("net_contents", "")
        ext = self.extracted.get("net_contents", "")
        
        ratio = fuzz.token_set_ratio(exp.lower(), ext.lower())
        if ratio >= threshold:
            return True, f"Match: Verified {ext}"
        return False, f"Mismatch: Expected '{exp}', Found '{ext}'"

    def verify_government_warning(self) -> tuple[bool, str]:
        """Enforces a strict, case-sensitive character verification layout."""
        ext = self.extracted.get("government_warning", "")
        
        #'GOVERNMENT WARNING:' header must be in all-caps
        if "GOVERNMENT WARNING:" not in ext:
            return False, "REJECTED: Mandatory 'GOVERNMENT WARNING:' header is missing or not in ALL CAPS."
            
        return True, "Match: Exact header and text verified."

    def run_compliance_check(self) -> dict:
        """Executes all rules and determines an overarching approval state."""
        brand_ok, brand_msg = self.verify_brand_name()
        abv_ok, abv_msg = self.verify_abv()
        net_ok, net_msg = self.verify_net_contents()
        warning_ok, warning_msg = self.verify_government_warning()
        
        is_approved = all([brand_ok, abv_ok, net_ok, warning_ok])
        
        return {
            "is_approved": is_approved,
            "details": {
                "brand_name": {"passed": brand_ok, "message": brand_msg},
                "abv": {"passed": abv_ok, "message": abv_msg},
                "net_contents": {"passed": net_ok, "message": net_msg},
                "government_warning": {"passed": warning_ok, "message": warning_msg}
            }
        }