import os # TODO: import sys?
from dotenv import load_dotenv
from src.graph import app

load_dotenv()

def main():
    print("--- 🌐 Ask-the-Web Agent (Local Llama 3.2) ---")
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        inputs = {"messages": [("user", user_input)]}
        
        # Stream updates to show the recruiter the Node-by-Node execution
        for output in app.stream(inputs, stream_mode="updates"):
            for node, data in output.items():
                print(f"\n[Node: {node.upper()}]")
                if "messages" in data:
                    last_msg = data["messages"][-1]
                    
                    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                        print(f"  Action: Calling {last_msg.tool_calls[0]['name']}")
                    elif last_msg.content:
                        print(f"  Assistant: {last_msg.content}")

if __name__ == "__main__":
    main()