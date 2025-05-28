import streamlit as st
import pdfplumber
from docx import Document
from chains import Chain

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

def main():
    st.title("Cold Mail Generator from Job URL & Resume Upload")

    name = st.text_input("Your Full Name", "John Doe")
    job_url = st.text_input("Job Posting URL")
    tone = st.selectbox("Select Tone for Email", ["Formal", "Casual", "Professional", "Friendly"])
    language = st.selectbox("Select Language", ["English"])
    
    resume_file = st.file_uploader("Upload your Resume (PDF or DOCX)", type=["pdf", "docx"])

    if st.button("Generate Cold Email"):
        if not name.strip() or not job_url.strip() or resume_file is None:
            st.error("Please provide your name, job URL, and upload your resume.")
            return

        # Extract resume text
        try:
            if resume_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(resume_file)
            elif resume_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = extract_text_from_docx(resume_file)
            else:
                st.error("Unsupported file format. Please upload PDF or DOCX.")
                return
        except Exception as e:
            st.error(f"Failed to extract resume text: {e}")
            return

        chain = Chain(name=name, tone=tone, resume_text=resume_text, language=language)
        
        try:
            job_description = chain.scrape_job_description(job_url)
        except Exception as e:
            st.error(f"Failed to scrape job URL: {e}")
            return

        email = chain.write_mail(job_description)
        st.subheader("Generated Cold Email")
        st.text_area("Email", email, height=350)

if __name__ == "__main__":
    main()
