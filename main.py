import discord,configparser,traceback,json,random,datetime,requests,time,asyncio
from commands import addtwitchstream,querystream,removetwitchstream
from functions import livestream,srsubmission,srapproval
from discord.ext import tasks,commands

config = configparser.ConfigParser()
config.read("./config.ini")
configdiscord = config["Discord"]

intents = discord.Intents.default()
client = commands.Bot(command_prefix=configdiscord["prefix"], intents=intents, help_command=None)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    await change_status()
    if not start_livestream.is_running():
        start_livestream.start()

    if not change_status.is_running():
        change_status.start()

    if not start_srcom.is_running():
        start_srcom.start()

@client.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def ping(ctx):
    if ctx.channel.name == "livestreams" or ctx.channel.name == "mods":
        await ctx.send("Pong!")

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def addstream(ctx,arg):
    try:
        check = addtwitchstream.main(arg)
        if check == 0:
            await ctx.send('{0} was added to the stream list.'.format(arg))
        elif check == 1:
            await ctx.send('{0} was already in the stream list.'.format(arg))
    except:
        errormsg = traceback.print_exc()
        admin = await client.get_user_info(int(configdiscord["admin"]))
        await client.send_message(admin, errormsg)
        await ctx.send('An error occurred when adding {0}.'.format(arg))

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def removestream(ctx,arg):
    try:
        check = removetwitchstream.main(arg)
        if check == 0:
            await ctx.send('{0} was removed to the stream list.'.format(arg))
        elif check == 1:
            await ctx.send('{0} was not found in the stream list'.format(arg))
    except:
        errormsg = traceback.print_exc()
        admin = await client.get_user_info(int(configdiscord["admin"]))
        await client.send_message(admin, errormsg)
        await ctx.send('An error occurred when removing {0}.'.format(arg))

@client.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def query(ctx,arg):
    try:
        check = querystream.main(arg)
        if check == 0:
            await ctx.send('{0} is in the stream list'.format(arg))
        elif check == 1:
            await ctx.send('{0} is not in the stream list.'.format(arg))
    except:
        errormsg = traceback.print_exc()
        admin = await client.get_user_info(int(configdiscord["admin"]))
        await client.send_message(admin, errormsg)
        await ctx.send('An error occurred when querying {0}.'.format(arg))

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        timeleft = round(error.retry_after)
        await ctx.send("This command is on cooldown, you can use it in {0} seconds".format(timeleft))

@tasks.loop(minutes=5)
async def start_livestream():
    gettime = time.localtime()
    gettime = time.strftime("%H:%M:%S", gettime)
    print("[{0}] [TWITCH] Starting Twitch livestream checks...".format(gettime))

    streamchannel = client.get_channel(int(configdiscord["streamchannel"]))

    loadjson = open("./json/streamlist.json", "r")
    streamlist = json.load(loadjson)
    loadjson.close()

    checkjson = open("./json/online.json", "r")
    checkonlinelist = json.load(checkjson)
    checkjson.close()

    for key in streamlist["Streams"]["Twitch"]:
        username = key["username"]

        breaker = 0
        for onlinekey in checkonlinelist["Online"]:
            onlineuser = onlinekey["username"]
            if username.lower() == onlineuser.lower():
                breaker = 1
                print("--- {0} is online... Skipping...".format(username))
                break

        if breaker == 0:
            online = livestream.execute(username)
            if online == 0 or online == None:
                pass
            else:
                embed=discord.Embed(title=online[2], url="https://twitch.tv/"+online[0], description="[Click here to watch](https://twitch.tv/{0})".format(online[0]), color=0x00c7fc, timestamp=datetime.datetime.utcnow())
                embed.set_author(name=online[0]+" is live on Twitch!", url="https://twitch.tv/"+online[0], icon_url=online[1])
                embed.add_field(name="Game", value=online[3], inline=True)
                embed.set_footer(text="THPSBot")
                embed.set_image(url=online[4])
                grabmessage = await streamchannel.send(embed=embed)

                onlinejson = open("./json/online.json", "r")
                onlinelist = json.load(onlinejson)
                jsonupdate = {"username":online[0],"messageid":grabmessage.id}
                onlinelist["Online"].append(jsonupdate)
                onlinejson.close()

                onlinejson = open("./json/online.json","w")
                onlinejson.write(json.dumps(onlinelist))
                onlinejson.close()

    checkjson = open("./json/online.json", "r")
    checkonlinelist = json.load(checkjson)
    checkjson.close()

    for key in checkonlinelist["Online"]:
        username = key["username"]
        messageid = key["messageid"]

        online = livestream.execute(username)
        if online == 0 or online == None:
            print("--- {0} has gone offline... Removing embed...".format(username))
            del key["username"]
            del key["messageid"]
            
            onlinejson = open("./json/online.json", "w")

            checkonlinelist = json.dumps(checkonlinelist).replace('{},','')
            checkonlinelist = checkonlinelist.replace(', {}', '')
            checkonlinelist = checkonlinelist.replace('{}','')

            onlinejson.write(checkonlinelist)
            onlinejson.close()

            messageid = int(messageid)

            finalid = await streamchannel.fetch_message(messageid)
            await finalid.delete()
        else:
            embed=discord.Embed(title=online[2], url="https://twitch.tv/"+online[0], description="[Click here to watch](https://twitch.tv/{0})".format(online[0]), color=0x00c7fc, timestamp=datetime.datetime.utcnow())
            embed.set_author(name=online[0]+" is live on Twitch!", url="https://twitch.tv/"+online[0], icon_url=online[1])
            embed.add_field(name="Game", value=online[3], inline=True)
            embed.set_footer(text="THPSBot")
            embed.set_image(url=online[4])

            editid = await streamchannel.fetch_message(messageid)
            await editid.edit(embed=embed)
    
    gettime = time.localtime()
    gettime = time.strftime("%H:%M:%S", gettime)
    print("[{0}] [TWITCH] Completed Twitch livestream checks...".format(gettime))

@tasks.loop(minutes=30)
async def change_status():
    try:
        gamelist = configdiscord["statusmessage"]
        gamelist = gamelist.split(',')
        gamelistcount = len(gamelist) -1
        gamenum = random.randint(0,gamelistcount)
        gettime = time.localtime()
        gettime = time.strftime("%H:%M:%S", gettime)
        print("[{0}] [BOT] Changing game status to {1}".format(gettime,gamelist[gamenum].replace('"',"").replace("]","").replace("[","").strip()))
        await client.change_presence(activity=discord.Game(name=gamelist[gamenum].replace('"',"").replace("]","").replace("[","").strip()))
    except:
        traceback.print_exc()

@tasks.loop(minutes=60)
async def start_srcom():
    gettime = time.localtime()
    gettime = time.strftime("%H:%M:%S", gettime)
    print("[{0}] [SRCOM] Checking Speedrun.com API for submissions...".format(gettime))
    submissionschannel = client.get_channel(int(configdiscord["subchannel"]))
    pbschannel = client.get_channel(int(configdiscord["pbchannel"]))
    #configspeedrun = config["SpeedrunCom"]

    loadjson = open("./json/submissions.json", "r")
    submissions = json.load(loadjson)
    loadjson.close()

    games = requests.get("https://speedrun.com/api/v1/series/tonyhawk/games").json()["data"]

    for game in games:
        runs = srsubmission.execute(game)
        if runs != 0:
            for run in runs:
                breaker = 0
                for submissionkey in submissions["Submitted"]:
                    if submissionkey["id"] == run["id"]:
                        breaker = 1
                        break

                if breaker == 0:
                    print("--- New submission found ({0})".format(run["id"]))
                    #verify = await submissionschannel.send("<@&{0}>".format(configspeedrun[runs[0]["abbr"]]))
                    embed=discord.Embed(title=run["game"], url=run["link"], description="{0} in {1}\nSubmitted: {2} UTC".format(run["cat"],run["time"],run["date"]), color=0x3498db, timestamp=datetime.datetime.utcnow())
                    if run["pfp"] == None: embed.set_author(name=run["player"], url=run["link"], icon_url="https://cdn.discordapp.com/attachments/83090266910621696/868581069492985946/3x.png")
                    else: embed.set_author(name=run["player"], url=run["link"], icon_url=run["pfp"])
                    embed.set_footer(text="THPSBot")
                    embed.set_thumbnail(url=run["cover"])
                    grabmessage = await submissionschannel.send(embed=embed)

                    onlinejson = open("./json/submissions.json", "r")
                    onlinelist = json.load(onlinejson)
                    #jsonupdate = {"id":run["id"],"verifyid":verify.id,"messageid":grabmessage.id,"player":run["player"],"game":run["game"],"link":run["link"],"pfp":run["pfp"],"cat":run["cat"],"time":run["time"],"cover":run["cover"]}
                    jsonupdate = {"id":run["id"],"messageid":grabmessage.id,"player":run["player"],"game":run["game"],"link":run["link"],"pfp":run["pfp"],"cat":run["cat"],"time":run["time"],"cover":run["cover"]}
                    onlinelist["Submitted"].append(jsonupdate)
                    onlinejson.close()

                    onlinejson = open("./json/submissions.json","w")
                    onlinejson.write(json.dumps(onlinelist))
                    onlinejson.close()

    loadjson = open("./json/submissions.json", "r")
    submissions = json.load(loadjson)
    loadjson.close()

    for key in submissions["Submitted"]:
        runid = key["id"]
        messageid = key["messageid"]
        #verifyid = key["verifyid"]

        print("--- Verifying status of {0}".format(runid))
        try:
            check = requests.get("https://speedrun.com/api/v1/runs/{0}".format(runid)).json()["data"]["status"]["status"]
        except:
            check = 0

        try:
            if check == "verified" or check == "rejected" or check == 0:
                if check == "verified":
                    print("--- {0} has been approved!".format(runid))
                    approval = srapproval.execute(runid)
                    
                    if approval[0] > 0:
                        if approval[2] == 0: subcatname = ""
                        else: subcatname = approval[2]
                        
                        if approval[0] == 1:
                            embed=discord.Embed(title="\U0001f3c6 NEW WORLD RECORD! \U0001f3c6", url=key["link"], description="{0}\n{1} {2} in {3}".format(key["game"],key["cat"],subcatname,key["time"]), color=0x3498db, timestamp=datetime.datetime.utcnow())
                        elif approval[0] == 2:
                            embed=discord.Embed(title="\U0001f948 NEW PERSONAL BEST! \U0001f948", url=key["link"], description="{0}\n{1} {2} in {3}".format(key["game"],key["cat"],subcatname,key["time"]), color=0x3498db, timestamp=datetime.datetime.utcnow())
                        elif approval[0] == 3:
                            embed=discord.Embed(title="\U0001f949 NEW PERSONAL BEST! \U0001f949", url=key["link"], description="{0}\n{1} {2} in {3}".format(key["game"],key["cat"],subcatname,key["time"]), color=0x3498db, timestamp=datetime.datetime.utcnow())
                        else:
                            embed=discord.Embed(title="NEW PERSONAL BEST!", url=key["link"], description="{0}\n{1} {2} in {3}".format(key["game"],key["cat"],subcatname,key["time"]), color=0x3498db, timestamp=datetime.datetime.utcnow())
                
                        if key["pfp"] == None: embed.set_author(name=key["player"], url=key["link"], icon_url="https://cdn.discordapp.com/attachments/83090266910621696/868581069492985946/3x.png")
                        else: embed.set_author(name=key["player"], url=key["link"], icon_url=key["pfp"])
                        embed.add_field(name="Placing", value=approval[0], inline=True)
                        embed.add_field(name="Points", value=approval[1], inline=True)
                        embed.set_footer(text="THPSBot")
                        embed.set_thumbnail(url=key["cover"])
                        await pbschannel.send(embed=embed)
                    else:
                        print("--- {0} is an obsolete submission.".format(runid))
                else:
                    print("--- {0} has been rejected or deleted...".format(runid))
                
                del key["id"]
                #del key["verifyid"]
                del key["messageid"]
                del key["player"]
                del key["link"]
                del key["game"]
                del key["cat"]
                del key["time"]
                del key["pfp"]
                del key["cover"]

                messageid = int(messageid)

                finalid = await submissionschannel.fetch_message(messageid)
                await finalid.delete()

                #finalid = await submissionschannel.fetch_message(verifyid)
                #await finalid.delete()
        except Exception as exception:
            print(exception)
        else:
            traceback.print_exc()

    onlinejson = open("./json/submissions.json", "w")

    submissions = json.dumps(submissions)
    submissions = submissions.replace('{}, ','').replace(', {}', '').replace('{}','')

    onlinejson.write(submissions)
    onlinejson.close()

client.run(configdiscord["distoken"])