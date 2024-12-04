import datetime
from flask import Flask, render_template, request, url_for
import webview
import os
import pickle
import argparse
import multiprocessing
import subprocess

"""
The program first reads for the required info stored in the ./data/data.dat binary file.
"""
app = Flask(__name__)
parser = argparse.ArgumentParser()
parser.add_argument("--type", type=str, required=False)
args = parser.parse_args()
with open(r"/usr/share/linuxDynamicWallpapers/data/data.dat", "rb") as fr:
    data = pickle.load(fr)


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == "static":
        filename = values.get("filename", None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values["q"] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


def setDEWallpaper(desktop_environment, style):
    if style in [
        "bitday",
        "firewatch",
        "gradient",
    ]:  # only these 3 types have .png file extension.
        type = ".png"
    else:
        type = ".jpg"

    if desktop_environment.lower() in [
        "/usr/share/xsessions/plasma",
        "plasmawayland",
        "neon",
        "plasma",
        "kde",
    ]:  # Set Wallpaper for Plasma DE
        print("Inside", desktop_environment)
        os.system(
            'qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript \'var allDesktops = desktops();print (allDesktops);for (i=0;i<allDesktops.length;i++) {d = allDesktops[i];d.wallpaperPlugin = "org.kde.image";d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");d.writeConfig("Image", "file:///usr/share/linuxDynamicWallpapers/images/'
            + style
            + "/"
            + str(datetime.datetime.now().hour)
            + type
            + "\")}'"
        )

    elif desktop_environment.lower() == "cinnamon":  # Set Wallpaper for Cinnamon DE
        print("Inside", desktop_environment)
        os.system(
            f'gsettings set org.cinnamon.desktop.background picture-uri "file:///usr/share/linuxDynamicWallpapers/images/{style}/{datetime.datetime.now().hour}'
            + f'{type}"'
        )

    elif desktop_environment.lower() in [
        "xfce session",
        "xfce",
        "xubuntu",
    ]:  # Set Wallpaper for XFCE DE
        print("Inside", desktop_environment)
        SCREEN = subprocess.getoutput(
            "echo $(xrandr --listactivemonitors | awk -F ' ' 'END {print $1}' | tr -d \:)"
        )
        MONITOR = subprocess.getoutput(
            "echo $(xrandr --listactivemonitors | awk -F ' ' 'END {print $2}' | tr -d \*+)"
        )
        os.system(
            f"xfconf-query --channel xfce4-desktop --property /backdrop/screen{SCREEN}/monitor{MONITOR}/workspace0/last-image --set usr/share/linuxDynamicWallpapers/images/{style}/{datetime.datetime.now().hour}"
            + f"{type}"
        )

    elif desktop_environment.lower() == "mate":  # Set Wallpaper for Mate DE
        print("Inside", desktop_environment)
        os.system(
            f"gsettings set org.mate.background picture-filename usr/share/linuxDynamicWallpapers/images/{style}/{datetime.datetime.now().hour}"
            + f"{type}"
        )

    elif desktop_environment.lower() == "lxde":  # Set Wallpaper for LXDE
        print("Inside", desktop_environment)
        os.system(
            f'pcmanfm --set-wallpaper="usr/share/linuxDynamicWallpapers/images/{style}/{datetime.datetime.now().hour}'
            + f'{type}"'
        )

    elif desktop_environment.lower() in [
        "pantheon",
        "gnome",
        "gnome-xorg",
        "ubuntu",
        "deepin",
    ]:  # Set Wallpaper for Ubuntu, Pop, Pantheon DE
        print("Inside", desktop_environment)
        os.system(
            f"gsettings set org.gnome.desktop.background picture-uri file:///usr/share/linuxDynamicWallpapers/images/{style}/{datetime.datetime.now().hour}"
            + f"{type}"
        )

    elif desktop_environment.lower() == "pop":
        print("Inside", desktop_environment)
        if (
            subprocess.getoutput("gsettings get org.gnome.desktop.interface gtk-theme")
            == "'Pop-dark'"
        ):
            os.system(
                f"gsettings set org.gnome.desktop.background picture-uri-dark file:///usr/share/linuxDynamicWallpapers/images/{style}/{datetime.datetime.now().hour}"
                + f"{type}"
            )
        else:
            os.system(
                f"gsettings set org.gnome.desktop.background picture-uri file:///usr/share/linuxDynamicWallpapers/images/{style}/{datetime.datetime.now().hour}"
                + f"{type}"
            )
    else:
        print("Inside", desktop_environment)
        os.system(
            f"feh --bg-fill usr/share/linuxDynamicWallpapers/images/{style}/{datetime.datetime.now().hour}"
            + f"{type}"
        )


@app.route("/")
def index():
    return render_template("index.html")  # Display the Flask Frontend.


@app.route("/setWallpaper")
def setWallpaper():
    wallpaper = request.args.get("wallpaper").lower()
    DE = subprocess.getoutput("echo $DESKTOP_SESSION")
    previousWallpaper = data["currentWallpaper"]
    print(previousWallpaper)
    setDEWallpaper(DE, wallpaper)
    data["DE"] = DE
    data["currentWallpaper"] = wallpaper
    with open("/usr/share/linuxDynamicWallpapers/data/data.dat", "wb") as fw:
        pickle.dump(data, fw)
    os.system(
        f'(crontab -u {subprocess.getoutput("whoami")} -l ; echo "0 * * * * env PATH={subprocess.getoutput("echo $PATH")} DISPLAY={subprocess.getoutput("echo $DISPLAY")} DESKTOP_SESSION={subprocess.getoutput("echo $DESKTOP_SESSION")} DBUS_SESSION_BUS_ADDRESS="{subprocess.getoutput("echo $DBUS_SESSION_BUS_ADDRESS")}" setdwl {wallpaper}") | crontab -u {subprocess.getoutput("whoami")} -'
    )  # Sets a cronjob for the wallpaper to change every hour.
    os.system(
        f'crontab -u {subprocess.getoutput("whoami")} -l | grep -v "{previousWallpaper}"  | crontab -u {subprocess.getoutput("whoami")} -'
    )
    os.system("/etc/init.d/cron reload")
    os.system(
        f'notify-send "Linux Dynamic Wallpapers" "Set wallpaper to {wallpaper.upper()}" '
    )


def runServer():
    app.run(port=6969)


def onclose():
    p1.kill()


if __name__ == "__main__":
    if args.type == None:  # For setting the Wallpaper using GUI
        p1 = multiprocessing.Process(target=runServer)
        p1.start()
        window = webview.create_window(
            "Linux Dynamic Wallpapers", "http://localhost:6969"
        )
        window.closing += onclose
        webview.start(http_server=True)
    else:
        with open(
            "/usr/share/linuxDynamicWallpapers/data/data.dat", "rb"
        ) as f:  # For changing the wallpaper every hour, managed by setdwl.sh
            data = pickle.load(f)
        setDEWallpaper(data["DE"], args.type)
