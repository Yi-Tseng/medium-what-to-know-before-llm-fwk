import requests
import dotenv
import os
dotenv.load_dotenv()

URL = "https://api.openai.com/v1"
LLM_MODEL = "gpt-4.1-mini"
API_KEY = os.environ["API_KEY"]

PROMPT = """
Answer the following questions as best you can. You have access to the following tools:

get_user_id(firstname, lastname)
get_shipping_records(user_id)

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [get_user_id, get_shipping_records]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: "Show me shopping records from Yi Tseng"
Thought:"""

resp = requests.post(f"{URL}/responses",
                     headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + API_KEY
                    },
                    json={
                        "model": LLM_MODEL,
                        "input": PROMPT
                    })

while resp.status_code == 200:
    resp = resp.json()
    output = resp["output"]
    if not output:
        print("No output from LLM, try again")
        break
    content = output[0]["content"][0]["text"]
    thought, action, action_input, tool_output = None, None, None, None
    final_answer = None
    lines = content.strip().split("\n")
    for line in lines:
        if "Thought:" in line and not thought: # we only pick first thought
            thought = line[8:].strip()
        elif "Action:" in line:
            action = line[7:].strip()
        elif "Action Input:" in line:
            action_input = line[13:].strip()
        elif "Final Answer:" in line:
            final_answer = line[13:].strip()
        elif thought is None:
            # It might output without "Thought: "
            thought = line.strip()
    print(f"Bot: {thought}")
    print(f"Bot Action {action} ({action_input})")

    if action == "get_user_id":
        tool_output = "12345678"
        print(f"Tool: getting user id with input {action_input} -> {tool_output}")
    elif action == "get_shipping_records":
        tool_output = "['apple', 'orange', 'cake']"
        print(f"Tool getting shipping records with input {action_input} -> {tool_output}")
    elif action is not None:
        print(f"Unknown tool {action}")
        tool_output = f"Unknown tool {action}"

    # We need to double check if there still an action
    if final_answer and not action:
        print(f"Bot: Final answer is:\n{final_answer}")
        break

    # Update prompt an continue
    PROMPT += thought + "\n"
    PROMPT += "Action: " + action + "\n"
    PROMPT += "Action Input: " + action_input + "\n"
    PROMPT += "Observation: " + tool_output + "\n"
    PROMPT += "Thought:"

    resp = requests.post(f"{URL}/responses",
                     headers={
                        "Content-Type": "application/json",
                        "Authorization": "Bearer " + API_KEY
                    },
                    json={
                        "model": LLM_MODEL,
                        "input": PROMPT,
                        "temperature": 0
                    })