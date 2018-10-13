import os
import json

path_result_json = os.path.join(os.getcwd(), "result", "json")

for fn in os.listdir(path_result_json):
    file_path = os.path.join(path_result_json, fn)

    json_copy = {}
    js = {}
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            js = json.loads(f.read().strip())
        except Exception as e:
            pass

    if js is not None and "childFieldsOfStudy" in js.keys():
        json_copy["childFieldsOfStudy"] = js["childFieldsOfStudy"]

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(json_copy))
