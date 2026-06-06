import streamlit as st
from vision_agent import extract_label_data
from matcher import LabelMatcher
from dotenv import load_dotenv

#load env 
load_dotenv()

st.set_page_config(page_title="TTB Label Verification", layout="wide")

#PoC sidebar with expected inputs since I dont have COlA data 
with st.sidebar:
    st.header("Application Data")
    st.write("Enter the details from the COLA application:")
    expected_brand = st.text_input("Brand Name", value="OLD TOM DISTILLERY")
    expected_class = st.text_input("Class/Type", value="Kentucky Straight Bourbon Whiskey")
    expected_abv = st.text_input("Alcohol Content", value="45% Alc./Vol. (90 Proof)")
    expected_net_contents = st.text_input("Net Contents", value="750 mL")

    expected_data = {
        "brand_name": expected_brand,
        "class_type": expected_class,
        "abv": expected_abv,
        "net_contents": expected_net_contents
    }

#ui
st.title("AI Label Verification Prototype")
st.write("Upload alcohol labels to automatically verify them against the application data.")

#upload pics
uploaded_files = st.file_uploader("Upload Label Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"Processing {len(uploaded_files)} label(s)...")
    st.divider()

    for file in uploaded_files:
        st.subheader(f"Results for: {file.name}")
        
        #layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image(file, caption="Uploaded Label", use_container_width=True)
            
        with col2:
            with st.spinner("Analyzing image..."):
                try:
                    image_bytes = file.getvalue()
                    extracted_pydantic = extract_label_data(image_bytes)
                    extracted_data = extracted_pydantic.model_dump()
                    
                    if extracted_data.get("image_unreadable"):
                        st.error("REJECTED: Image is unreadable.")
                        st.divider()
                        continue

                    matcher = LabelMatcher(expected=expected_data, extracted=extracted_data)
                    results = matcher.run_compliance_check()
                    
                    if results["is_approved"]:
                        st.success("APPROVED: All critical fields match")
                    else:
                        st.error("REJECTED: One or more fields failed verification")
                        
                    st.markdown("### Field Breakdown")
                    
                    for field, details in results["details"].items():
                        formatted_field = field.replace('_', ' ').title()
                        if details["passed"]:
                            st.success(f"**{formatted_field}:** {details['message']}")
                        else:
                            st.error(f"**{formatted_field}:** {details['message']}")
                            
                    #ai thinking 
                    with st.expander("View Raw AI Extraction Data"):
                        st.json(extracted_data)

                except Exception as e:
                    st.error(f"An error occurred during processing. Please ensure your OPENAI_API_KEY is set in the .env file. \n\nError details: {str(e)}")
            
        st.divider()