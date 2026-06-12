"""
Medical AI - Multispecialty Agent
===================================
Upload a PDF medical report and get parallel analysis from six specialist
AI agents: Cardiologist, Psychologist, Pulmonologist, Neurologist,
Endocrinologist, and Immunologist. A final Multidisciplinary Agent
synthesizes all outputs into a unified diagnosis.
"""

import os
import io
import fitz  # PyMuPDF
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SPECIALIST_PROMPTS = {
    "Cardiologist": """Act like a cardiologist. You will receive a medical report of a patient.
Task: Review the patient's cardiac workup, including ECG, blood tests, Holter monitor results, and echocardiogram.
Focus: Determine if there are any subtle signs of cardiac issues. Rule out arrhythmias or structural abnormalities.
Recommendation: Provide guidance on further cardiac testing or management strategies.
Please only return the possible causes of symptoms and recommended next steps.
Medical Report: {medical_report}""",

    "Psychologist": """Act like a psychologist. You will receive a patient's report.
Task: Review the patient's report and provide a psychological assessment.
Focus: Identify potential mental health issues such as anxiety, depression, or trauma.
Recommendation: Offer guidance on therapy, counseling, or other interventions.
Please only return possible mental health issues and recommended next steps.
Patient's Report: {medical_report}""",

    "Pulmonologist": """Act like a pulmonologist. You will receive a patient's report.
Task: Review the report and provide a pulmonary assessment.
Focus: Identify respiratory issues such as asthma, COPD, or lung infections.
Recommendation: Suggest pulmonary function tests, imaging studies, or other interventions.
Please only return possible respiratory issues and recommended next steps.
Patient's Report: {medical_report}""",

    "Neurologist": """Act like a neurologist. You will receive a patient's medical report.
Task: Review the neurological assessment including CT scans, MRI results, and relevant tests.
Focus: Identify neurological disorders such as strokes, epilepsy, or neurodegenerative diseases.
Recommendation: Provide guidance on further neurological testing or potential treatments.
Please return potential neurological diagnoses and next steps.
Medical Report: {medical_report}""",

    "Endocrinologist": """Act like an endocrinologist. You will receive a medical report of a patient.
Task: Review the endocrine system assessment including thyroid, insulin, and cortisol levels.
Focus: Identify endocrine disorders such as diabetes, thyroid dysfunction, or adrenal disorders.
Recommendation: Provide guidance on further testing, diagnosis, and treatment strategies.
Please return possible endocrine-related diagnoses and next steps.
Medical Report: {medical_report}""",

    "Immunologist": """Act like an immunologist. You will receive a medical report of a patient.
Task: Review the immune system evaluation including tests for autoimmunity, allergies, or immunodeficiencies.
Focus: Identify immune system disorders such as autoimmune diseases or allergic reactions.
Recommendation: Provide guidance on further immune testing, diagnosis, or treatment plans.
Please return possible immune-related disorders and recommended next steps.
Medical Report: {medical_report}""",
}

SYNTHESIS_PROMPT = """Act like a multidisciplinary team of healthcare professionals.
You will receive medical reports from a Cardiologist, Psychologist, Pulmonologist, Neurologist, Endocrinologist, and Immunologist.
Task: Analyze all specialist reports and identify the 3 most likely health issues.
Return a concise bullet-point list of 3 possible health issues with reasoning for each.

Cardiologist Report: {cardiologist_report}
Psychologist Report: {psychologist_report}
Pulmonologist Report: {pulmonologist_report}
Neurologist Report: {neurologist_report}
Endocrinologist Report: {endocrinologist_report}
Immunologist Report: {immunologist_report}"""

SPECIALIST_COLORS = {
    "Cardiologist":    "#FFE4E4",
    "Psychologist":    "#E4F0FF",
    "Pulmonologist":   "#E4FFE4",
    "Neurologist":     "#FFF4E4",
    "Endocrinologist": "#F4E4FF",
    "Immunologist":    "#E4FFF4",
}


def read_pdf(uploaded_file) -> str:
    data = uploaded_file.read()
    doc = fitz.open(stream=data, filetype="pdf")
    return "".join(page.get_text("text") for page in doc)


def run_specialist(specialist: str, medical_report: str, model) -> tuple[str, str]:
    template = PromptTemplate.from_template(SPECIALIST_PROMPTS[specialist])
    chain = template | model
    result = chain.invoke({"medical_report": medical_report})
    return specialist, result.content


def run_synthesis(responses: dict, model) -> str:
    template = PromptTemplate.from_template(SYNTHESIS_PROMPT)
    chain = template | model
    result = chain.invoke({
        "cardiologist_report":    responses["Cardiologist"],
        "psychologist_report":    responses["Psychologist"],
        "pulmonologist_report":   responses["Pulmonologist"],
        "neurologist_report":     responses["Neurologist"],
        "endocrinologist_report": responses["Endocrinologist"],
        "immunologist_report":    responses["Immunologist"],
    })
    return result.content


# ── Streamlit UI ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="Medical AI - Multispecialty Agent", page_icon="🧠", layout="wide")

st.title("🧠 Medical AI - Multispecialty Agent")
st.markdown("Upload a medical report PDF. Six specialist AI agents analyze it in parallel and generate a unified multidisciplinary diagnosis.")

uploaded_file = st.file_uploader("Upload Medical Report PDF", type=["pdf"])

if uploaded_file:
    with st.expander("📄 Extracted Medical Report", expanded=True):
        with st.spinner("Reading PDF..."):
            medical_report = read_pdf(uploaded_file)
        st.text_area("Patient Report", value=medical_report, height=200, disabled=True)

    if st.button("Run Diagnosis", type="primary"):
        if not OPENAI_API_KEY:
            st.error("Set the OPENAI_API_KEY environment variable to run the agents.")
            st.stop()

        model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0125", api_key=OPENAI_API_KEY)
        responses = {}

        st.markdown("### Specialist Reports")
        progress = st.progress(0, text="Running specialist agents in parallel...")

        cols = st.columns(2)
        specialist_list = list(SPECIALIST_PROMPTS.keys())
        placeholders = {s: cols[i % 2].empty() for i, s in enumerate(specialist_list)}

        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(run_specialist, s, medical_report, model): s
                for s in specialist_list
            }
            completed = 0
            for future in as_completed(futures):
                specialist, response = future.result()
                responses[specialist] = response
                completed += 1
                progress.progress(completed / len(specialist_list), text=f"Completed: {specialist}")
                color = SPECIALIST_COLORS.get(specialist, "#F9F9F9")
                placeholders[specialist].markdown(
                    f"""<div style="background:{color};border-radius:12px;padding:1rem;margin-bottom:.5rem">
                    <strong>{specialist}</strong><br><small>{response}</small></div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("### Final Multidisciplinary Diagnosis")
        with st.spinner("Synthesizing all specialist reports..."):
            final_diagnosis = run_synthesis(responses, model)

        st.success(final_diagnosis)

        report_text = "MULTIDISCIPLINARY DIAGNOSIS REPORT\n" + "=" * 40 + "\n\n"
        for s, r in responses.items():
            report_text += f"{s.upper()}\n{'-' * len(s)}\n{r}\n\n"
        report_text += "FINAL DIAGNOSIS\n" + "-" * 15 + "\n" + final_diagnosis

        st.download_button(
            label="Download Full Report",
            data=report_text,
            file_name="multispecialty_diagnosis.txt",
            mime="text/plain",
        )
