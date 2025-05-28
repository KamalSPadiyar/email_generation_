from dotenv import load_dotenv
import os

load_dotenv()
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

class Chain:
    def __init__(self, name="John Doe", tone="Formal", resume_text="", language="English"):
        self.name = name
        self.tone = tone
        self.resume_text = resume_text
        self.language = language
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama3-70b-8192"
        )

    def scrape_job_description(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            for script in soup(["script", "style"]):
                script.extract()

            text = soup.get_text(separator="\n")
            lines = [line.strip() for line in text.splitlines()]
            text = "\n".join(line for line in lines if line)
            return text
        except Exception as e:
            raise RuntimeError(f"Failed to scrape URL: {e}")

    def write_mail(self, job_description):
        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### CANDIDATE DETAILS:
            Name: {user_name}
            Resume Summary: {resume_text}
            Tone: {tone_style}
            Language: {language}

            ### INSTRUCTION:
            Write a concise and personalized cold email applying for the job described above.
            Use the candidate's name and tone style.
            Highlight relevant experience from the resume.
            Use the specified language.
            ### EMAIL ONLY:
            """
        )
        chain_email = prompt_email | self.llm | RunnableLambda(lambda x: x.content)
        email_text = chain_email.invoke({
            "job_description": job_description,
            "user_name": self.name,
            "resume_text": self.resume_text,
            "tone_style": self.tone,
            "language": self.language
        })
        return email_text
