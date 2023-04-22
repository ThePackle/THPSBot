import aiosqlite

async def main(arg):
    async with aiosqlite.connect("dbs/streamlist.db") as connect:
        cursor = await connect.cursor()
        await cursor.execute("SELECT text FROM twitch WHERE UPPER(text) LIKE ?", (arg.upper(),)) 

        if(await cursor.fetchone() == None):
            await cursor.execute("INSERT INTO twitch VALUES (?,?)",(None, arg))
            await connect.commit()
            return 0
        else:
            return 1