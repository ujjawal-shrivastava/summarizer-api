import json
import requests

async def worker(text:str,token:str, endpoint:str, flag:bool=False):
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "inputs":text,
        "options":{
            "use_cache":True
        }
    }

    response = requests.request("POST", endpoint, headers=headers, data=json.dumps(payload))
    output = json.loads(response.content.decode("utf-8"))
    return output[0]["summary_text" if flag else "generated_text"]
