import sqlite3


def shifr(a):
    return 17 * (13 + int(bin((((a * 5 + 1) * 2 - 3) * 7 + 1) // 2)[2:]))


def deshifr(s):
    a = int(s)
    a //= 17
    a -= 13
    b = int(str(a), 2)
    b *= 2
    b -= 1
    b //= 7
    b += 3
    b //= 2
    b -= 1
    b //= 5
    return b

def save_id():
    f = open("BattleSkies.redacc", mode="w", encoding="utf-8")
    print("loginned", file=f)
    print(shifr(id), file=f)
    f.close()

def update_money():
    pass

def clear_sessions():
    global id, con
    cur = con.cursor()
    cur.execute(f"DELETE FROM `session` WHERE `player` = {id}")
    con.commit()
    lst = cur.execute(f"SELECT `id` FROM `games`").fetchall()
    for el in lst:
        idg = el[0]
        k = len(cur.execute(f"SELECT * FROM `session` WHERE `game` = {idg}").fetchall())
        if k == 0:
            cur.execute(f"DELETE FROM `games` WHERE `id` = {idg}")
            cur.execute(f"DELETE FROM `shouting` WHERE `game` = {idg}")
            cur.execute(f"DELETE FROM `explosions` WHERE `game` = {idg}")
    con.commit()

def add_money(n):
    global money, con, id
    money += n
    cur = con.cursor()
    cur.execute(f"UPDATE `users` SET `money` = {money} WHERE `id` = {id}")

id = 0
con = sqlite3.connect("BattleSkies.db")
money = 0
images_count = 80
plane = 0
