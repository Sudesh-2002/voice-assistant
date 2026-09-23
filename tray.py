import threading
from PIL import Image, ImageDraw
import pystray


def _make_icon() -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.ellipse([2, 2, size - 2, size - 2], fill=(30, 100, 220, 255))

    draw.ellipse([14, 10, size - 18, size - 22], fill=(80, 160, 255, 120))

    draw.text((22, 18), "A", fill=(255, 255, 255, 255))

    return img


def run_tray(stop_event: threading.Event):
    
    icon_image = _make_icon()

    def on_quit(icon, item):
        print("[Atlas] Quit requested from tray.")
        stop_event.set()
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("Atlas is listening", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", on_quit),
    )

    icon = pystray.Icon(
        name="Atlas",
        icon=icon_image,
        title="Atlas — Voice Assistant",
        menu=menu,
    )

    icon.run()