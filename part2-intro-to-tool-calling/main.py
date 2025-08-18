import requests
import json

SYSTEM_PROMPT = """You are a helpful assistant that can use various tools.

You MUST answer the question if you are able to answer the original question from previous chat messages.

Here are tools you can use:
The first tool is called "find_username", which has a parameter "user_id". This tool can search for specific user with user id.
The second tool is called "add_user", which has a parameter "username". This tool can add a user to the system.

If you need to use a tool, you MUST respond in the JSON format {"name": "the name of tool", "parameters": a dictionary of argument name and its value}.

The system will provide the tool call result to you if you are trying to call a tool."""

messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

while True:
    user_input = input("user> ")
    messages.append({
        "role": "user",
        "content": user_input
    })
    resp = requests.post(
        "http://127.0.0.1:11434/api/chat",
        headers={
            "Content-Type": "application/json"
        },
        json={
            "model": "gemma3:4b-it-fp16",
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0
            }
        }
    )

    if resp.status_code != 200:
        print(f"Error when getting response: code {resp.status_code}")
        break
    resp = resp.json()
    assistant_msg = resp["message"]["content"]
    messages.append({
        "role": "assistant",
        "content": assistant_msg
    })

    # response might surrand between "```json" and "```", we need to remove that first
    if assistant_msg.strip().startswith("```json"):
        assistant_msg = assistant_msg.strip()[7:]
        if assistant_msg.endswith("```"):
            assistant_msg = assistant_msg[:-3].strip()

    try:
        tool_call = json.loads(assistant_msg)
        tool_name = tool_call["name"]
        params = tool_call["parameters"]
        print(f"code> LLM want to call tool {tool_name} with parameter {params}")
        # Let's use a fixed result here, but it can calls a python function
        # or just run some code.
        if tool_name == "find_username":
            user_id = params["user_id"]
            result = f"system: Username of user id {user_id} is \"yi1234\""
        elif tool_name == "add_user":
            username = params["username"]
            result = f"system: User {username} added"
        else:
            result = f"system: Unknown tool \"{tool_name}\""
        messages.append({
            "role": "user",
            "content": result
        })

        # Once we provide the tool call result, we will
        # let the LLM use the result to answer the question.
        resp = requests.post(
            "http://127.0.0.1:11434/api/chat",
            headers={
                "Content-Type": "application/json"
            },
            json={
                "model": "gemma3:4b-it-fp16",
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0
                }
            }
        )
        if resp.status_code != 200:
            print(f"Error when getting response: code {resp.status_code}")
            break
        resp = resp.json()
        assistant_msg = resp["message"]["content"]
        messages.append({
            "role": "assistant",
            "content": assistant_msg
        })
        print(f"assistant> {assistant_msg}")
    except:
        # Not a valid JSON, assume it is not tool call message
        # We can print the message here

        print(f"assistant> {assistant_msg}")
