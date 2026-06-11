import streamlit as st
from google import genai
from pdf2image import convert_from_bytes
import json

# ---------- PAGE SETTINGS ----------
st.set_page_config(page_title="AI CV Parser", page_icon="📄")
st.title("📄 AI-Powered CV Parser")

# ---------- SIDEBAR ----------
api_key = st.sidebar.text_input(
    "Enter Gemini API Key",
    type="password"
)

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader(
    "Upload Resume PDF",
    type=["pdf"]
)

# ---------- BUTTON ----------
if st.button("Parse Resume"):

    if not api_key:
        st.error("Please enter Gemini API Key.")
        st.stop()

    if uploaded_file is None:
        st.error("Please upload a PDF file.")
        st.stop()

    try:
        # ---------- PDF → IMAGES ----------
        pages = convert_from_bytes(
            uploaded_file.read(),
            poppler_path=r"C:\poppler-26.02.0\Library\bin"
        )

        st.success(f"{len(pages)} page(s) loaded.")

        # ---------- NEW GEMINI CLIENT ----------
        client = genai.Client(api_key=api_key)

        prompt = """
Analyze this resume and extract information.

Return ONLY valid JSON in this format:

{
  "personal_information": {},
  "education": [],
  "work_experience": [],
  "certifications": [],
  "projects": [],
  "skills": [],
  "languages": []
}
"""

        contents = [prompt]
        contents.extend(pages)

        with st.spinner("Analyzing Resume..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents
            )

        result = response.text.strip()
        result = result.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(result)

            st.success("Resume Parsed Successfully ✅")
            st.json(data)

            st.download_button(
                "Download JSON",
                data=json.dumps(data, indent=4),
                file_name="resume_data.json",
                mime="application/json"
            )

        except Exception:
            st.warning("AI ne valid JSON return nahi kiya")
            st.code(result)

    except Exception as e:
        st.error(str(e))