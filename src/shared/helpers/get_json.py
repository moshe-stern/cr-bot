from flask import Request


def get_json(request: Request):
    data = request.get_json()
    if not data:
        raise Exception("error: No JSON data found in the request.")
    file = data.get("file")
    if not file or "$content" not in file:
        raise Exception("error: No file content found in the request.")
    instance = data.get("instance")
    if not instance:
        raise Exception("error: Missing 'instance' field in the request.")
    update_type = data.get("type")
    if not update_type:
        raise Exception("error: Missing 'type' field in the request.")
    return data
