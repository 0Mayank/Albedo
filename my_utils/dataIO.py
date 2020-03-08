import json


def change_value(file: str, value: str, changeto: str):
    try:
        with open(file, "r") as jsonFile:
            data = json.load(jsonFile)
    except FileNotFoundError:
        raise FileNotFoundError("The file you tried to get does not exist...")

    data[value] = changeto
    with open(file, "w") as jsonFile:
        json.dump(data, jsonFile, indent=2)


def append_value(file: str, value: str, addition: str):
    try:
        with open(file, "r") as jsonFile:
            data = json.load(jsonFile)
    except FileNotFoundError:
        raise FileNotFoundError("The file you tried to get does not exist...")

    data[value].append(addition)
    with open(file, "w") as jsonFile:
        json.dump(data, jsonFile, indent=2)

def backup_states(state_instance):
    D = json.dumps(state_instance, default=lambda x: x.__dict__)
    with open('json/states.json', "w") as f:
        json.dump(D, f)

def recover_states(state_instance):
    try:    
        with open(f"json/states.json") as f:
                D = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("The file you tried to get does not exist...")

    D = json.loads(D)
    for guild_id, settings in D.get("states").items():
        guild = state_instance.get_state(int(guild_id))
        for setting, value in settings.items():
            guild.set_var(setting, value)
