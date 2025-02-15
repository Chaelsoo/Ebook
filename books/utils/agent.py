from typing import Dict, Any
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from typing import Optional
from helpers import create_token_payment

def get_env_value(key: str, default: Any, convert_type: callable) -> Any:
    """Helper function to safely get and convert environment variables."""
    try:
        return convert_type(os.getenv(key, default))
    except (ValueError, TypeError) as e:
        print(f"Error converting {key}: {e}. Using default value: {default}")
        return convert_type(default)

# Load environment variables
load_dotenv()

# Initialize LLM with better error handling
try:
    llm = ChatGoogleGenerativeAI(
        model=os.getenv("GENAI_MODEL", "gemini-1.5-flash"),
        temperature=get_env_value("GENAI_TEMPERATURE", 0, float),
        max_tokens=get_env_value("GENAI_MAX_TOKENS", 1024, int),
        timeout=get_env_value("GENAI_TIMEOUT", 60, int),
        max_retries=get_env_value("GENAI_MAX_RETRIES", 5, int),
    )
except Exception as e:
    raise RuntimeError(f"Failed to initialize ChatGoogleGenerativeAI: {e}")

# Tool Input Schemas

class PurchaseArgs(BaseModel):
    product_isbn: str = Field(description="the isbn of the book")

# Tools Implementation
@tool(args_schema=PurchaseArgs)
def make_purchase(product_isbn:str):
    TEST_TOKEN = "tok_visa"
    token=TEST_TOKEN,
    price_id = "price_1QseOSLtFIt5rFjlgmW7B7rk"
    customer_email = "benhibafodhil@gmail.com"
    """Make a purchase with the given name."""
    create_token_payment(price_id, token, customer_email)
    return f"Purchase made for {customer_email}"


# Define available tools
tools = [
    make_purchase
]

def create_agent() -> AgentExecutor:
    """
    Creates and configures the agent executor.
    
    Returns:
        AgentExecutor: Configured agent executor
    """
    try:
        # Pull the prompt template
        prompt = hub.pull("hwchase17/openai-tools-agent")
        
        # Create the agent
        agent = create_tool_calling_agent(
            llm=llm,
            tools=tools,
            prompt=prompt,
        )
        
        # Create and return the agent executor
        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,  # Add maximum iterations to prevent infinite loops
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create agent: {e}")

def run_agent_query(agent_executor: AgentExecutor, query: str) -> Dict[str, Any]:
    """
    Runs a query through the agent executor with error handling.
    
    Args:
        agent_executor (AgentExecutor): The configured agent executor
        query (str): The query to process
        
    Returns:
        Dict[str, Any]: The agent's response
    """
    try:
        return agent_executor.invoke({"input": query})
    except Exception as e:
        print(f"Error processing query '{query}': {e}")
        return {"error": str(e)}

# def main():
#     """Main function to run the agent with sample queries."""
#     try:
        # # Create the agent executor
        # agent_executor = create_agent()
        
        # # Test queries

        # while True:
        #     query = input("Enter a query: ")
        #     if query == "exit":
        #         break
        #     response = run_agent_query(agent_executor, query)
        #     print(f"\nQuery: {query}")
        #     print(f"Response: {response}")
        

#     except Exception as e:
#         print(f"Error in main execution: {e}")

# if __name__ == "__main__":
#     main()