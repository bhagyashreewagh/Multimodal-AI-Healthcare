# Multimodal AI Healthcare

Upload a PDF medical report and get parallel analysis from six specialist AI agents. A final Multidisciplinary Agent synthesizes all outputs into a unified diagnosis.

---

## What it does

Most medical reports are written for one specialist at a time. This system runs six specialist agents in parallel against the same report and combines their findings — surfacing cross-domain patterns that a single-specialist analysis would miss.

**Upload a PDF. Get a multidisciplinary diagnosis in under a minute.**

---

## Specialist Agents

| Agent | Focus |
|---|---|
| Cardiologist | ECG, blood tests, cardiac risk factors, arrhythmias |
| Psychologist | Mental health indicators, anxiety, depression, trauma |
| Pulmonologist | Respiratory function, asthma, COPD, lung infections |
| Neurologist | CT/MRI findings, neurological disorders, cognitive markers |
| Endocrinologist | Thyroid, insulin, cortisol, metabolic disorders |
| Immunologist | Autoimmunity, allergies, immunodeficiencies |

All six run simultaneously via `ThreadPoolExecutor`. A final **Multidisciplinary Agent** aggregates their outputs and identifies the 3 most likely health issues with reasoning.

---

## Running the App

```bash
pip install -r requirements.txt

export OPENAI_API_KEY=your_key_here
streamlit run app.py
```

Open http://localhost:8501, upload a PDF, and click **Run Diagnosis**.

A sample report is included: `sample_report_1.pdf`

---

## Repo Structure

```
app.py                    Streamlit UI (upload, parallel agents, synthesis, download)
Codefile_GitHub.ipynb     Original notebook with agent definitions
requirements.txt
sample_report_1.pdf       Sample medical report for testing
Homescreen.png            UI screenshot
Outputreport.png          Output screenshot
```

---

## Architecture

```
PDF Upload
    |
    v
PyMuPDF text extraction
    |
    v (passed to all agents simultaneously)
+--------+  +--------+  +--------+  +--------+  +--------+  +--------+
| Cardio |  | Psych  |  | Pulmo  |  | Neuro  |  | Endo   |  | Immuno |
+--------+  +--------+  +--------+  +--------+  +--------+  +--------+
         \       |           |           |          |        /
          +------+-----------+-----------+----------+-------+
                                    |
                                    v
                     Multidisciplinary Synthesis Agent
                                    |
                                    v
                        Final Diagnosis + Download
```

---

## Tech Stack

- Python
- Streamlit (UI)
- LangChain + OpenAI GPT-3.5 Turbo (agent orchestration)
- PyMuPDF / fitz (PDF extraction)
- ThreadPoolExecutor (parallel agent execution)

---

## Disclaimer

This system is for research and educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment.
