import aiosqlite

async def main(type,tuple):
    async with aiosqlite.connect("dbs/streamlist.db") as connect:
        cursor = await connect.cursor()
        if type == 0:
            await cursor.execute("SELECT text FROM exemptions")
            streamlist = await cursor.fetchall()
            streamlist = [row[0].casefold() for row in streamlist]
            return streamlist
        elif type == 1:
            await cursor.execute("INSERT INTO exemptions (text) VALUES (?)", (tuple,))
        elif type == 2:
            await cursor.execute(f"DELETE FROM exemptions WHERE id = '{tuple}'")
        elif type == 3:
            await cursor.execute("SELECT text FROM youtube")
            streamlist = cursor.fetchall()
            streamlist = [row[0].casefold() for row in streamlist]
            return streamlist
        elif type == 4:
            await cursor.execute("INSERT INTO youtube (text) VALUES (?)", (tuple,))
        elif type == 5:
            await cursor.execute(f"DELETE FROM youtube WHERE id = '{tuple}'")

        await connect.commit()