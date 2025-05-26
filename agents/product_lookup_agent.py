import os
import sys

#Hack to fix issue wit this file not being able to see the tools.tools.py file for some reason below)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
from tools.tools import get_pricing_url_tavily
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain.agents import (create_react_agent, AgentExecutor)
from langchain import hub


def lookup(company: str) -> str:
    llm = ChatOpenAI(
        temperature=0,
        model=os.getenv("MODEL_VERSION"),
        api_key=os.getenv("2DMOPEN_API_KEY")
    )

    query = """{company_name} is a software company that charges per user per month.
                I want you to:
                 1) Find the name and price of 2 of their products.
                Your answer should just contain the name of the product and the price on each line.
                2) For each of the 2 products list 2 benefits to copmanies and users of these products.
                Your answer should just contain the name of the product and the benefit on each line"""
    
    prompt_template = PromptTemplate(
        template=query, input_variable=["company_name"]
    )

    tools_for_agent = [
        Tool(
            name = "Crawl Web for Product information",
            func = get_pricing_url_tavily,
            description="""
                You must use this tool to search for product pricing and benefits for a company.

                Instructions:
                - Input should be a company name (e.g., "Hubspot").
                - Output must include:
                    - Product (name)
                    - Price
                    - Benefit (list of two strings)
                    - Marketing Blurb (6 words only)
                - You are not allowed to invent new actions.
                - If uncertain, retry.

                Expected structure:
                Final Answer: {{
                "summary": "...",
                "products": [
                    {{
                    "Product": "...",
                    "Price": "...",
                    "Benefit": ["...", "..."],
                    "Marketing Blurb": "..."
                    }},
                    ...
                ]
                }}
            """

        )
    ]

    react_prompt = hub.pull("hwchase17/react")

    agent = create_react_agent(llm=llm,tools=tools_for_agent,prompt=react_prompt)
    agent_executor = AgentExecutor(agent=agent,tools=tools_for_agent,handle_parsing_errors=True,allowed_tools=["Crawl Web for Product information"], verbose=True)

    result = agent_executor.invoke(
        input = {"input": prompt_template.format_prompt(company_name=company)}
    )

    product_info = result["output"]
    return product_info


if __name__== "__main__":
    pricing_url = lookup(company="salesforce")
    print(pricing_url)
