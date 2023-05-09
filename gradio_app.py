import gradio as gr
from openai_llm import get_openai_result
import re
import json
import requests
import os


pieces_json_path = 'pieces.json'

token = os.getenv('TOKEN')
url_base_path = "http://13.233.191.14:3000/v1/"
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'{token}'
}

def run_pieces_requests(endpoint, type, headers, payload):
    url = f"{url_base_path}{endpoint}"
    try:
        response = requests.request(type, url, headers=headers, data=payload)
        response.raise_for_status()
        return json.loads(response.text)
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        raise
    except requests.exceptions.ConnectionError as errc:
        print(f"Connection Error: {errc}")
        raise
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
        raise
    except requests.exceptions.RequestException as err:
        print(f"Unknown Error: {err}")
        raise

def find_object_by_name(json_data, name):
    for obj in json_data:
        if obj['name'] == name:
            endpoint = f"pieces/{obj['name']}?version={obj['version']}"
            p_details = run_pieces_requests(endpoint, 'GET', headers, {})
            return p_details
    return None

def add_text(history, text):
    history = history + [(text, None)]
    return history, ""

def add_file(history, file):
    history = history + [((file.name,), None)]
    return history


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def extract_trigger_action(input_string: str):
    trigger_pattern = r'"trigger":\s*\[([^]]+)]'
    action_pattern = r'"action":\s*\[([^]]+)]'

    trigger_match = re.search(trigger_pattern, input_string)
    action_match = re.search(action_pattern, input_string)

    trigger_array = []
    action_array = []

    if trigger_match:
        trigger_string = trigger_match.group(1)
        trigger_array = [item.strip('"') for item in trigger_string.split(',')]

    if action_match:
        action_string = action_match.group(1)
        action_array = [item.strip('"') for item in action_string.split(',')]

    return trigger_array, action_array


def create_flow(flow_name="new_flow", collectionId="5JAHklNOpdQDZOkU8g4hV"):
    endpoint = 'flows'
    payload = json.dumps({
        "displayName": flow_name,
        "collectionId": collectionId
    })
    created_flow = run_pieces_requests(endpoint, 'POST', headers, payload)
    return created_flow['id']

def update_trigger(flow_id, trigger_details):
    endpoint = f'flows/{flow_id}'
    payload = json.dumps({
        "type": "UPDATE_TRIGGER",
        "request": {
            "name": "trigger",
            "displayName": "Trigger",
            "type": "PIECE_TRIGGER",
            "valid": False,
            "settings": {
                "pieceName": trigger_details['name'],
                "pieceVersion": trigger_details['version'],
                "triggerName": "",
                "input": {},
                "inputUiInfo": {
                    "currentSelectedData": ""
                }
            }
        }
    })
    output = run_pieces_requests(endpoint, 'POST', headers, payload)
    return output

def add_action(flow_id, step_number, action_details):
    print(action_details)
    endpoint = f'flows/{flow_id}'
    if(step_number == 0):
        parent_step = "trigger"
        next_step = "step_1"
    else:
        parent_step = f"step_{step_number}"
        next_step = f"step_{step_number+1}"
    payload = json.dumps({
        "type": "ADD_ACTION",
        "request": {
            "parentStep": parent_step,
            "action": {
                "name": next_step,
                "displayName": action_details['displayName'],
                "valid": False,
                "type": "PIECE",
                "settings": {
                    "pieceName": action_details['name'],
                    "pieceVersion": action_details['version'],
                    "input": {},
                    "inputUiInfo": {
                        "customizedInputs": {}
                    }
                }
            }
        }
    })
    output = run_pieces_requests(endpoint, 'POST', headers, payload)
    return output


def bot(history):
    prompt = history[-1][0]
    print(prompt)
    response = get_openai_result(prompt, "base")
    
    trigger, actions = extract_trigger_action(response)
    print(f"Trigger: {trigger}")
    print(f"Action: {actions}")
    if not trigger and not actions:
        history[-1][1] = response
        return history

    json_data = read_json_file(pieces_json_path)
    piece_obj = find_object_by_name(json_data, trigger[0])
    actions_objs = []
    for act in actions:

        act_obj = find_object_by_name(json_data, act)
        actions_objs.append(act_obj)
    
    flow_id = create_flow()
    print(flow_id)

    update_trigger(flow_id, piece_obj)

    for i, aobj in enumerate(actions_objs):
        add_action(flow_id, i, aobj)


    history[-1][1] = f"Automation task is added! Your flow ID: {flow_id}"
    return history

with gr.Blocks() as demo:
    chatbot = gr.Chatbot([], elem_id="chatbot").style(height=650)

    with gr.Row():
        txt = gr.Textbox(
                show_label=False,
                placeholder="Enter text and press ⏎",
            ).style(container=False)
       

        txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
            bot, chatbot, chatbot
        )
demo.launch()
