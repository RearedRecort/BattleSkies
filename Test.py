import arcade
from pve import PveView

def main():
    window = arcade.Window(1920, 1080, "PVE Test", fullscreen=False)
    view = PveView("F-15", 960, 540)
    window.show_view(view)
    arcade.run()

if __name__ == "__main__":
    main()