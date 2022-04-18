import configparser,traceback
from twitchAPI.twitch import Twitch

def execute(username):
    config = configparser.ConfigParser()
    config.read("./config.ini")
    configtwitch = config["Twitch"]

    ttvid = configtwitch["ttvid"]
    ttvtoken = configtwitch["ttvtoken"]

    try: 
        twitch = Twitch(ttvid,ttvtoken)
        export = twitch.get_streams(user_login=username)["data"]
    except: 
        print("--- Server error occurred... Skipping round...")

    try:
        for i in export:
            streamgame  = i["game_name"]
            if not streamgame in configtwitch["ttvgames"]:
                return

            streamtitle = i["title"]
            streamtnail = i["thumbnail_url"].replace("{width}","1280").replace("{height}","720")

        export1 = twitch.get_users(logins=username)["data"]

        for i in export1:
            streamname  = i["display_name"]
            streampfp   = i["profile_image_url"]

    except:
        traceback.print_exc()

    try:
        return [streamname,streampfp,streamtitle,streamgame,streamtnail]
    except:
        return 0