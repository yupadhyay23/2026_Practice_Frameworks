# AUTHOR: Yash Upadhyay
# AI_Framework_LangGraph
# LAST MODIFIED: JAN 16, 2026

# We import these packages so we can store our API key securely in an .env file
# as well as import necessary packages to design our framework in LangGraph
from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
import sys #Imported so that user can exit our program once they are donwe posing queries


load_dotenv()

llm = init_chat_model( # Set LLM model to gpt-4o
    "openai:gpt-4o"
)

#Structered output fomrat
class MessageClassifer(BaseModel): 
    message_type: Literal["financial", "email", "human resources", "web search"] = Field(
        ...,
        description="Classify if the message requires a financial answer or email answer or human resources answer or a web search answer"
    )


class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str| None # Tracks messages in list format
    next: str|None

def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(MessageClassifer) # Matches pydantic model
    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
            - 'financial': if it asks for anything needing a financial point of view to answer it
            - 'email': if it asks for explicit help with emails
            - 'human resources': if it asks for something that can be answered by human resources expertise
            - 'web search': if it asks for something that cannot be answered by a financial or email or human resources expertise
            """
        },
        {"role": "user", "content": last_message.content} 
    ])
    
    return {"message_type": result.message_type}
  
  
     
def router(state: State):
    message_type = state.get("message_type", "web search")
    if message_type == "financial":
        return {"next": "financial"}
    
    if message_type == "email":
        return {"next": "email"}
    
    if message_type == "human resources":
        return {"next": "human resources"}
    
    return {"next": "web search"}



def hr_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """Analyze employee data, policies, or organizational trends
                       and provide insights or actionable recommendations. """
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}



def financial_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """Examine financial data related to the question, including budgets,
                 revenues, and expenditures for 2026.
                Identify any anomalies or trends. """
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}



def web_search_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """Search the web for relevant, up-to-date information on the user's question.
                   Focus on credible sources and highlight key findings. """
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}



def email_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
         "content": """ Help the user with composing an email, be professional and ask follow up 
                         questions to help the user. """
         },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}
    
graph_builder = StateGraph(State)

graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("financial", financial_agent)
graph_builder.add_node("email", email_agent)
graph_builder.add_node("web search", web_search_agent)
graph_builder.add_node("human resources", hr_agent)

graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")
graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"financial" : "financial", "email": "email", "web search":"web search", "human resources":"human resources"}
)
graph_builder.add_edge("financial", END)
graph_builder.add_edge("email", END)
graph_builder.add_edge("human resources", END)
graph_builder.add_edge("web search", END)

# To make a node on the graph, write a function


graph = graph_builder.compile()

def run_chatbot():
    state = {"messages": [], "message_type": None}
    
    print("Enter 'exit' to quit the program at any point")
    while True:
        user_input = input("User: ")
        
        if user_input == "exit":
            print("Agent: Bye")
            sys.exit(0)
        
        state["messages"] = state.get("messages", []) + [
            {"role": "user", "content": user_input}
        ]
        
        state = graph.invoke(state)
        
        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")

if __name__ == "__main__":
    run_chatbot()           
  
user_input = input("Enter a message: ")
state = graph.invoke({"messages": [{"role": "user", "content" : user_input}]})


print(state["messages"][-1].content)    