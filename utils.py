import os
import json

def all_cases(za_word):
    if len(za_word) == 1:
        if za_word.isalnum():
            return [za_word.lower(), za_word.upper()]
        else:
            return[za_word]
    else:
        output = []
        f = za_word[0]
        l = za_word[1:]
        for st in all_cases(l):
            if f.isalnum():
                output.append(f.lower() + st)
                output.append(f.upper() + st)
            else:
                output.append(f+st)
        return output

def save(jsonfile, data):
    with open(jsonfile, "w") as f:
      json.dump(data, f, indent=4)

def retrieve(jsonfile):
    with open(jsonfile, "r") as f:
       data = json.load(f)
    return data

def delete(file, jsonFile, keyName):
    os.remove(file)
    data = retrieve(jsonFile)
    to_delete = data[keyName]
    to_delete.remove(file)
    data[keyName] = to_delete
    save(jsonFile, data)

def format_seconds(time_seconds):
    """Formats some number of seconds into a string of format d days, x hours, y minutes, z seconds"""
    seconds = time_seconds
    hours = 0
    minutes = 0
    days = 0
    while seconds >= 60:
        if seconds >= 60 * 60 * 24:
            seconds -= 60 * 60 * 24
            days += 1
        elif seconds >= 60 * 60:
            seconds -= 60 * 60
            hours += 1
        elif seconds >= 60:
            seconds -= 60
            minutes += 1

    return f"{days}d {hours}h {minutes}m {seconds}s"

    