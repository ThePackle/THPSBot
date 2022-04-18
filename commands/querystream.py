import json

def main(arg):
    loadjson = open("./json/streamlist.json", "r")
    streamlist = json.load(loadjson)

    for key in streamlist["Streams"]["Twitch"]:
        username = key["username"]

        if username.lower() == arg.lower():
            return 0
    
    loadjson.close()

    return 1