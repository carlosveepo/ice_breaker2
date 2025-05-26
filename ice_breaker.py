from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import sys
#Hack to fix issue wit this file not being able to see the tools.tools.py file for some reason below)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dotenv import load_dotenv
load_dotenv()
from agents.product_lookup_agent import lookup as product_lookup_agent
from output_parsers import Summary, summary_parser


def ice_break_with(company: str) -> Summary:
    product_list =  product_lookup_agent(company=company)

    summary_template = """
        Given these products and prices {information} from a company:
        1. Reprint the information in structured JSON format, with **each product** containing:
        - Product
        - Price
        - Benefit (list of two strings)
        - Marketing Blurb (required, 6 words only)
        2. Ensure that each product includes all fields. 
        \n{format_instructions}
        """
    
    summary_prompt_template = PromptTemplate(input_variables=["information"], 
                                             template=summary_template,
                                             partial_variables={"format_instructions": summary_parser.get_format_instructions() })

    llm = ChatOpenAI(temperature=0, model=os.getenv("MODEL_VERSION"),api_key=os.getenv("2DMOPEN_API_KEY"))

    #chain = summary_prompt_template | llm
    chain = summary_prompt_template | llm | summary_parser

    res:Summary = chain.invoke(input={"information": product_list})
    print("Agent output:")
    #print(product_list)
    print("Final output")
    #print(res)
    return res

if __name__ == "__main__":
    
    print("Ice Breaker Start")
    ice_break_with(company="Hubspot")

    