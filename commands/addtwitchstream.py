import json

def main(arg):
    loadjson = open("./json/streamlist.json", "r")
    streamlist = json.load(loadjson)

    for key in streamlist["Streams"]["Twitch"]:
        username = key["username"]

        if username == arg:
            return 1
    
    jsonupdate = {"username":arg}
    streamlist["Streams"]["Twitch"].append(jsonupdate)

    loadjson.close()
    loadjson = open("./json/streamlist.json", "w")
    loadjson.write(json.dumps(streamlist))
    loadjson.close()

    return 0