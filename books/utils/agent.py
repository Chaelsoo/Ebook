from dotenv import load_dotenv
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    create_react_agent,
)
from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv()
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GENAI_MODEL", "gemini-1.5-flash"),
    temperature=float(os.getenv("GENAI_TEMPERATURE", 0)),
    max_tokens=int(os.getenv("GENAI_MAX_TOKENS", 1024)),
    timeout=int(os.getenv("GENAI_TIMEOUT", 60)),
    max_retries=int(os.getenv("GENAI_MAX_RETRIES", 1)),
)

from helpers import create_token_payment  # Move import to top of file


def make_purchase(*args, **kwargs):
    """Make a purchase with the given price ID and customer email."""  # Move docstring before function parameters
    price_id = "price_1QseOSLtFIt5rFjlgmW7B7rk"
    customer_email = "benhibafodhil@gmail.com"
    result = create_token_payment(price_id, customer_email)
    print(result)  # Consider using logging instead of print
    return f"Purchase made for {customer_email}"

tools = [
    Tool(
        name="make purchase",
        func=make_purchase,
        description="Used when the user wants to make a purchase",
    )
]

prompt = hub.pull("hwchase17/react")

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt,
    stop_sequence=True,  # This parameter might not be needed or could cause issues
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
)

try:
    while True:
        user_input = input("You: ")
        if not user_input.strip():  # Add input validation
            print("Please enter a valid input")
            continue
        
        response = agent_executor.invoke({"input": user_input})
        print("Agent:", response)
except KeyboardInterrupt:
    print("\nExiting...")