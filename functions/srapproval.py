import requests,math
from math import exp

def execute(runid):
    print("--- [SRCOM] Evaluating submission approval.")
    runinfo = requests.get("https://speedrun.com/api/v1/runs/{0}".format(runid)).json()["data"]

    gameid = runinfo["game"]
    catid = runinfo["category"]
    levelid = runinfo["level"]
    variables = runinfo["values"]

    if levelid == None:
        if len(variables) == 0:
            lb = requests.get("https://speedrun.com/api/v1/leaderboards/{0}/category/{1}".format(gameid,catid)).json()["data"]["runs"]
            subcatname = 0
        else:
            lbline = ""
            subcatname = ""
            for key in variables:
                keyvar = variables.get(key)
                subcat = "var-{0}={1}&".format(key,keyvar)

                subcatadd = requests.get("https://speedrun.com/api/v1/variables/{0}".format(key)).json()["data"]["values"]["values"][keyvar]["label"]

                subcatname += "{0}, ".format(subcatadd)

                lbline = lbline + subcat
            
            subcatname = "(" + subcatname[:-2] + ")"
            lbline = lbline[:-1]

            lb = requests.get("https://speedrun.com/api/v1/leaderboards/{0}/category/{1}?{2}".format(gameid,catid,lbline)).json()["data"]["runs"]
    else:
        lb = requests.get("https://speedrun.com/api/v1/leaderboards/{0}/level/{1}/{2}".format(gameid,levelid,catid)).json()["data"]["runs"]

        subcatname = requests.get("https://speedrun.com/api/v1/levels/{0}".format(levelid)).json()["data"]["name"]

        subcatname = "(" + subcatname + ")"

    wr = lb[0]
    wrsec = wr["run"]["times"]["primary_t"]

    for run in lb:
        if runid == run["run"]["id"]:
            place = run["place"]
            pbsec = run["run"]["times"]["primary_t"]

            ratio = 4.8284 * (wrsec/pbsec)
            if levelid == None:
                points = math.trunc(0.008 * exp(ratio) * 1000)
            else:
                points = math.trunc(0.008 * exp(ratio) * 100)
            
            pass


    try: return place,points,subcatname
    except UnboundLocalError: return 0,0,0