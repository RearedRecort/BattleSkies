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

id = 0
con = sqlite3.connect("BattleSkies.db")
