import sys
import os

from termcolor import cprint
from pyfiglet import figlet_format
from colorama import init


def show_logo():
    os.system("cls")
    init(strip=not sys.stdout.isatty())
    print("\n")
    logo = figlet_format("JamBit", font="banner3")
    cprint(logo, "light_cyan")
    print("")


def show_dev_info():
    print("\033[36m" + "VERSION: " + "\033[34m" + "1.0" + "\033[34m")
    print("\033[36m" + "DEV: " + "\033[34m" + "https://t.me/JamBitPY" + "\033[34m")
    print(
        "\033[36m"
        + "GitHub: "
        + "\033[34m"
        + "https://github.com/Jaammerr"
        + "\033[34m"
    )
    print(
        "\033[36m"
        + "DONATION EVM ADDRESS: "
        + "\033[34m"
        + "0x08e3fdbb830ee591c0533C5E58f937D312b07198"
        + "\033[0m"
    )
    print()


def load_console() -> None:
    show_logo()
    show_dev_info()
