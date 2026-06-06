# AI-Powered Alcohol Label Verification App (Prototype)

## Executive Summary & Problem Context
The Bureau of Alcohol, Tobacco, Firearms and Explosives Compliance Division processes roughly 150,000 Certificate of Label Approval (COLA) applications annually with a lean team of 47 agents. Review processes are highly manual, forcing agents to perform mundane data entry verification rather than complex compliance analysis. 

This standalone proof-of-concept delivers an automated, agentic verification system built specifically to address core stakeholder criteria:
* **Operational Velocity:** Processes images and returns data in under 5 seconds to prevent workflow abandonment.
* **Accessible Design:** Built with a clean, intuitive interface tailored to users with varying technical comfort levels.
* **High-Volume Ingestion:** Built-in batch processing capabilities to alleviate application backlogs during peak seasons.

---

## Technical Architecture & Core Stack

The system leverages a modern, decoupled agentic stack chosen for rapid deployment and rigorous data structure enforcement:

* **Frontend & Application Flow (`app.py`):** Utilizes **Streamlit** to deliver a straightforward, linear user experience that requires zero navigation training. Supports asynchronous multi-file native batch uploads.
* **Orchestration & Data Extraction Agent (`vision_agent.py`):** Developed using **LangChain** and **Pydantic**. Rather than chaining multiple rigid OCR libraries and regex cleaners, it employs a deterministic, single-pass multimodal vision model (`gpt-4o-mini`) configured at `temperature=0.0`. It utilizes LangChain's structured output mechanism to guarantee an immutable schema payload.
* **Compliance Evaluation Logic (`matcher.py`):** A custom business logic matrix that applies tiered verification rules based on domain requirements.

### **Tiered Verification Matrix**

| Target Field | Strategy | Justification |
| :--- | :--- | :--- |
| **Brand Name** & **Net Contents** | Fuzzy Levenshtein Distance (`thefuzz`) | Evaluates semantic match over structural format, preventing false rejections for casing or punctuation variance (e.g., verifying "STONE'S THROW" against "Stone's Throw"). |
| **Alcohol Content (ABV)** | Regular Expression Isolation | Extracts numeric payloads out of strings to accurately compare values, remaining agnostic to syntax style (e.g., matching "45% Alc./Vol." with "45%"). |
| **Government Warning** | Strict Case-Sensitive Character Matching | Enforces zero-tolerance validation. Instantly rejects the label if the mandatory header `"GOVERNMENT WARNING:"` is missing or not fully capitalized. |

---

## Technical Trade-offs & Production Considerations

While this prototype serves as a standalone proof of concept, transition to a federal production environment requires addressing infrastructure limitations noted by IT Systems Administration:

> **Network & Firewall Restrictions:** Government infrastructure frequently restricts outbound cloud API traffic, which previously disrupted scanning vendor pilots. 

* **Prototype Trade-off:** Cloud vision APIs were utilized here to demonstrate cutting-edge extraction capabilities and maintain processing speeds under the 5-second baseline.
* **Production Migration Path:** Because the orchestration layer is built cleanly on LangChain, the backend can effortlessly swap out the cloud-based LLM provider for a self-hosted, on-premise open-source vision model (such as a fine-tuned Llama-3-Vision variant) running inside a secure, FedRAMP-certified private network enclave.

---

## Setup & Local Installation

### **Prerequisites**
* Python 3.10 or higher
* An active OpenAI API Key

### **Installation Instructions**

1. Clone or download this project repository to your local machine.
2. Open a terminal inside the root project directory and install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and append your API credentials:
   ```text
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```
4. Fire up the local application server:
   ```bash
   streamlit run app.py
   ```
5. The interface will open automatically in your browser at `http://localhost:8501`.

---

## Future Enhancements
* **Computer Vision Pre-processing:** Integrating an active pipeline filter (via OpenCV) to dynamically adjust brightness, reduce glare, and deskew images prior to LLM analysis to further enhance data ingestion accuracy.
* **Mock COLA Database Pre-fills:** Creating an internal dropdown menu of standard test cases to allow agents to seamlessly auto-populate form fields for benchmarking.