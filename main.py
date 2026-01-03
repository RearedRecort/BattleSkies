import arcade
import vars
from start import StartView


def main():
    try:
        file = open("BattleSkies.redacc", mode="r")
        s = file.readline().strip()
        if s == "loginned":
            id = int(file.readline().strip())
            vars.id = vars.deshifr(id)
        else:
            pass
        file.close()
    except Exception:
        file = open("BattleSkies.redacc", mode="w")
        print('unloginned', file=file)
        print(0, file=file)
        file.close()
    window = arcade.Window(fullscreen=True, title="Боевые небеса")
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
