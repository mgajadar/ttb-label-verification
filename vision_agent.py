import base64
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

class LabelData(BaseModel):
    """Structured data extracted from an alcohol beverage label"""
    brand_name: str = Field(description="The brand name printed on the label. Extract exactly as written")
    class_type: str = Field(description="The class/type designation (e.g. 'Kentucky Straight Bourbon Whiskey', 'Wine')")
    abv: str = Field(description="The alcohol content or ABV (e.g. '45% Alc./Vol.').")
    net_contents: str = Field(description="The volume measurement of the bottle contents (e.g. '750 mL')")
    government_warning: str = Field(description="The Government Health Warning Statement exactly as it appears")
    image_unreadable: bool = Field(
        description="Set to True ONLY if severe glare/blurry/extreme angles/poor lighting makes the text unreadable"
    )

def extract_label_data(image_bytes: bytes) -> LabelData:
    """
    Converts raw image bytes to a base64 string and uses a LangChain-managed 
    vision model pipeline to extract structured label fields
    """
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    #gpt 4o mini for < 5second constraint 
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    
    structured_llm = llm.with_structured_output(LabelData)
    
    message = HumanMessage(
        content=[
            {
                "type": "text", 
                "text": (
                    "You are an expert federal compliance data-entry tool for the TTB. "
                    "Analyze the provided image of an alcohol beverage label. "
                    "Extract the required compliance fields textually, character-for-character, "
                    "without assuming or normalizing abbreviations. "
                    "If the image is completely unreadable due to glare or environmental factors, "
                    "flag 'image_unreadable' as true."
                )
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
        ]
    )

    result = structured_llm.invoke([message])
    return result