from textwrap import dedent
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Correctly load the Google API key from an environment variable
#google_api_key = os.getenv("GOOGLE_API_KEY")  # This should be the name of your environment variable
google_api_key = "sua chave aqui"
# Set gemini pro as llm
llm = ChatGoogleGenerativeAI(
    model="gemini-pro", verbose=True, temperature=0.9, google_api_key=google_api_key
)

class Agents():
    def senior_engineer_agent(self):
        return Agent(
            role='Senior Software Engineer',
            goal='Create smart contract as needed',
            backstory=dedent("""\
                You are a Senior Software Engineer at a leading tech think tank.
                Your expertise in programming of the smart contracts and do your best to
                produce perfect code"""),
            allow_delegation=False,
            llm=llm,
            verbose=True
        )

    def qa_engineer_agent(self):
        return Agent(
            role='Software Quality Control Engineer',
            goal='create prefect smart contract, by analyzing the code that is given for errors',
            backstory=dedent("""\
                You are a software engineer that specializes in checking and audit code
                for errors. You have an eye for detail and a knack for finding
                hidden bugs.
                You check for missing imports, variable declarations, mismatched
                brackets and syntax errors.
                You also check for security vulnerabilities, and logic errors"""),
            allow_delegation=False,
            llm=llm,
            verbose=True
        )

	
