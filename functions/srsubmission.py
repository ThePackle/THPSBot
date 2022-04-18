import requests,datetime
from requests.structures import CaseInsensitiveDict

def execute(game):
    gameid = game["id"]

    runs = requests.get("https://speedrun.com/api/v1/runs?status=new&game={0}".format(gameid)).json()["data"]
    
    if len(runs) >= 1:
        final = []
        for run in runs:
            runid = run["id"]
            runlink = run["weblink"]

            print("--- [SRCOM] Found {0}.".format(runid))
            
            playerreq = requests.get("https://speedrun.com/api/v1/users/{0}".format(run["players"][0]["id"])).json()["data"]
            runplayer = playerreq["names"]["international"]
            runpfp = playerreq["assets"]["image"]["uri"]
            
            runcat = requests.get("https://speedrun.com/api/v1/categories/{0}".format(run["category"])).json()["data"]["name"]
            rundate = datetime.datetime.fromisoformat(run["submitted"].replace("Z","")).strftime("%B %-d, %Y @ %-H:%-M:%-S")

            runtime = run["times"]["primary_t"]
            runtime = str(datetime.timedelta(seconds=runtime))
            if "." in runtime:
                runtime = runtime[:-3]

            gameinfo = requests.get("https://speedrun.com/api/v1/games/{0}".format(gameid)).json()["data"]
            gameabbr = gameinfo["abbreviation"]
            gamename = gameinfo["names"]["international"]
            gamecover = gameinfo["assets"]["cover-large"]["uri"]

            export = {"id":runid,"player":runplayer,"pfp":runpfp,"game":gamename,"abbr":gameabbr,"link":runlink,"cat":runcat,"date":rundate,"time":runtime,"cover":gamecover}

            final.append(export)
    else:
        final = 0
    
    return final