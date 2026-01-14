import arcade
import vars
from start import StartView


def main():
    try:
        file = open("BattleSkies.redacc", mode="r")
        s = file.readline().strip()
        if s == "loginned":
            id = int(vars.deshifr(file.readline().strip()))
            cur = vars.con.cursor()
            vars.money = cur.execute(f"SELECT * FROM `users` WHERE `id` = '{id}'").fetchall()[0][0]
            vars.id = id
        else:
            vars.money = int(vars.deshifr(file.readline().strip()))
        file.close()
    except Exception:
        file = open("BattleSkies.redacc", mode="w")
        print('unloginned', file=file)
        print(0, file=file)
        file.close()
    window = arcade.Window(width=800, height=600, title="Боевые небеса")
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
