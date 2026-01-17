from PIL import Image


SKIN_MAP = {
    0: "F-15",
    1: "F-16",
    2: "J-35",
    3: "J-39",
    4: "MiG-31",
    5: "Mig-29",
    6: "Su-27",
    7: "Su-47",
}


for el in SKIN_MAP:
    im = Image.open(f"{SKIN_MAP[el]}.png")
    im2 = im.transpose(Image.FLIP_LEFT_RIGHT)
    im2.save(f'{SKIN_MAP[el]}-f.png')