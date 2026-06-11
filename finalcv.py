import streamlit as st
from google import genai
from pdf2image import convert_from_bytes
import json
import re

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="AI Resume Parser",
    layout="wide"
)

st.title("AI Resume Parser")

st.write(
    "Upload Resume PDF and convert into JSON"
)

# ==========================
# API KEY INPUT
# ==========================

api_key = st.sidebar.text_input(
    "Enter Gemini API Key",
    type="password"
)

# ==========================
# FILE UPLOAD
# ==========================

uploaded_file = st.file_uploader(
    "Upload Resume PDF",
    type=["pdf"]
)

# ==========================
# PDF -> IMAGE FUNCTION
# ==========================

def pdf_to_images(pdf_file):

    try:

        images = convert_from_bytes(
            pdf_file.read()
        )

        return images

    except Exception as e:

        st.error(
            f"PDF conversion error: {e}"
        )

        return []


# ==========================
# PARSE FUNCTION
# ==========================

def parse_resume(images, api_key):

    client = genai.Client(
        api_key=api_key
    )

    prompt = """
Extract resume information.

Return ONLY valid JSON.

Format:

{
  "personal_information": {
      "name":"",
      "email":"",
      "phone":"",
      "linkedin":""
  },

  "education": [],

  "work_experience": [],

  "certifications": [],

  "projects": []
}
"""

    contents = [prompt]

    for img in images:

        contents.append(img)

    response = client.models.generate_content(

        model="gemini-2.5-flash",

        contents=contents
    )

    return response.text


# ==========================
# CLEAN JSON
# ==========================

def extract_json(text):

    try:

        text = text.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        )

        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )

        if match:

            return json.loads(
                match.group(0)
            )

        return None

    except Exception:

        return None


# ==========================
# MAIN APP LOGIC
# ==========================

if uploaded_file:

    if not api_key:

        st.error(
            "Please enter Gemini API key"
        )

        st.stop()

    st.success(
        "PDF Uploaded Successfully"
    )

    if st.button(
        "Parse Resume"
    ):

        with st.spinner(
            "Converting PDF..."
        ):

            images = pdf_to_images(
                uploaded_file
            )

        if len(images) == 0:

            st.stop()

        with st.spinner(
            "AI analyzing..."
        ):

            try:

                raw_output = parse_resume(
                    images,
                    api_key
                )

            except Exception as e:

                st.error(
                    f"AI Error: {e}"
                )

                st.stop()

        st.subheader(
            "Raw Output"
        )

        st.text(
            raw_output
        )

        json_data = extract_json(
            raw_output
        )

        st.subheader(
            "Structured JSON"
        )

        if json_data:

            st.json(
                json_data
            )

            json_string = json.dumps(
                json_data,
                indent=4,
                ensure_ascii=False
            )

            st.download_button(

                label="Download JSON",

                data=json_string,

                file_name="resume.json",

                mime="application/json"
            )

        else:

            st.error(
                "JSON Parsing Failed"
            )