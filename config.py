# Copyright (c) 2020 Diego Roccia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import socket

import yaml
from libqtile import bar
from libqtile import hook
from libqtile import layout
from libqtile import widget
from libqtile.command import lazy
from libqtile.config import Click
from libqtile.config import Drag
from libqtile.config import DropDown
from libqtile.config import Group
from libqtile.config import Key
from libqtile.config import ScratchPad
from libqtile.config import Screen
from Xlib import display as xdisplay


class Colors:
    dark0_hard = "#1d2021"
    dark0 = "#282828"
    dark0_soft = "#32302f"
    dark1 = "#3c3836"
    dark2 = "#504945"
    dark3 = "#665c54"
    dark4 = "#7c6f64"
    dark4_256 = "#7c6f64"
    gray_245 = "#928374"
    gray_244 = "#928374"
    light0_hard = "#f9f5d7"
    light0 = "#fbf1c7"
    light0_soft = "#f2e5bc"
    light1 = "#ebdbb2"
    light2 = "#d5c4a1"
    light3 = "#bdae93"
    light4 = "#a89984"
    light4_256 = "#a89984"
    bright_red = "#fb4934"
    bright_green = "#b8bb26"
    bright_yellow = "#fabd2f"
    bright_blue = "#83a598"
    bright_purple = "#d3869b"
    bright_aqua = "#8ec07c"
    bright_orange = "#fe8019"
    neutral_red = "#cc241d"
    neutral_green = "#98971a"
    neutral_yellow = "#d79921"
    neutral_blue = "#458588"
    neutral_purple = "#b16286"
    neutral_aqua = "#689d6a"
    neutral_orange = "#d65d0e"
    faded_red = "#9d0006"
    faded_green = "#79740e"
    faded_yellow = "#b57614"
    faded_blue = "#076678"
    faded_purple = "#8f3f71"
    faded_aqua = "#427b58"
    faded_orange = "#af3a03"


accent_left = Colors.bright_blue
accent_right = Colors.bright_orange
font = "NovaMono for Powerline"

panel_height = 40
panel_font_size = 18

widget_defaults = dict(
    font=font, padding=0, fontsize=panel_font_size, borderwidth=0
)

# this import requires python-xlib to be installed


def get_num_monitors():
    num_monitors = 0
    try:
        display = xdisplay.Display()
        screen = display.screen()
        resources = screen.root.xrandr_get_screen_resources()

        for output in resources.outputs:
            monitor = display.xrandr_get_output_info(
                output, resources.config_timestamp
            )
            preferred = False
            if hasattr(monitor, "preferred"):
                preferred = monitor.preferred
            elif hasattr(monitor, "num_preferred"):
                preferred = monitor.num_preferred
            if preferred:
                num_monitors += 1
    except Exception:
        # always setup at least one monitor
        return 1
    else:
        return num_monitors


num_monitors = get_num_monitors()


def powerline_arrow(direction, color1, color2):
    if direction == "r":
        return [
            widget.TextBox(
                text=u"\ue0b0",
                foreground=color1,
                background=color2,
                fontsize=panel_height,
            ),
            widget.Sep(padding=5, linewidth=0, background=color2),
        ]
    else:
        return [
            widget.Sep(padding=14, linewidth=0, background=color1),
            widget.TextBox(
                text=u"\ue0b2",
                foreground=color2,
                background=color1,
                fontsize=panel_height,
            ),
        ]


def get_panel(monitor_id):
    widgets = [
        widget.TextBox(
            text=" " + socket.gethostname(),
            background=accent_left,
            foreground="#000000",
        ),
        *powerline_arrow("r", accent_left, Colors.dark1),
        widget.GroupBox(
            rounded=False,
            inactive=Colors.dark4,
            background=Colors.dark1,
            highlight_method="line",
            highlight_color=Colors.dark1,
            this_current_screen_border=accent_left,
            borderwidth=4,
            font="Font Awesome 5 Free,Font Awesome 5 Free Solid:style=Solid",
        ),
        *powerline_arrow("r", Colors.dark1, None),
        widget.WindowName(foreground="a0a0a0"),
        *powerline_arrow("l", None, Colors.dark1),
    ]

    if monitor_id == 0:
        widgets.append(
            widget.Systray(icon_size=24, background=Colors.dark1, padding=5)
        )

    widgets.extend(
        [
            widget.Sep(padding=5, linewidth=0, background=Colors.dark1),
            widget.Volume(borderwidth=0, background=Colors.dark1, emoji=True),
            *powerline_arrow("l", Colors.dark1, Colors.dark2),
            widget.Battery(
                energy_now_file="charge_now",
                energy_full_file="charge_full",
                power_now_file="current_now",
                update_delay=5,
                background=Colors.dark2,
                borderwidth=0,
            ),
            *powerline_arrow("l", Colors.dark2, Colors.dark4),
            widget.GenPollUrl(
                url="http://wttr.in?format=1",
                parse=lambda x: x.strip("\n"),
                json=False,
                foreground="#000000",
                background=Colors.dark4,
            ),
            *powerline_arrow("l", Colors.dark4, accent_right),
            widget.Clock(
                foreground="#000000",
                background=accent_right,
                format="%Y-%m-%d %H:%M",
            ),
            widget.TextBox(
                text=u" \ue0b2",
                foreground=Colors.bright_red,
                background=accent_right,
                fontsize=panel_height,
            ),
        ]
    )

    return bar.Bar(
        widgets, size=panel_height, background=Colors.dark0_hard, opacity=0.9
    )


screens = []

for m in range(num_monitors):
    screens.append(Screen(top=get_panel(m)))


# @hook.subscribe.screen_change
# def restart_on_randr(ev):
#    libqtile.qtile.cmd_restart()


@hook.subscribe.client_new
def dialogs(window):
    if (
        window.window.get_wm_type() == "dialog"
        or window.window.get_wm_transient_for()
    ):
        window.floating = True


@hook.subscribe.client_new
def float_steam(window):
    wm_class = window.window.get_wm_class()
    w_name = window.window.get_name()
    if wm_class == ("Steam", "Steam") and (
        w_name != "Steam"
        # w_name == "Friends List"
        # or w_name == "Screenshot Uploader"
        # or w_name.startswith("Steam - News")
        or "PMaxSize" in window.window.get_wm_normal_hints().get("flags", ())
    ):
        window.floating = True


@hook.subscribe.client_new
def float_firefox(window):
    wm_class = window.window.get_wm_class()
    w_name = window.window.get_name()
    if wm_class == ("Places", "firefox") and w_name == "Library":
        window.floating = True


@lazy.function
def float_to_front(qtile):
    for group in qtile.groups:
        for window in group.windows:
            if window.floating:
                window.cmd_bring_to_front()


mod = "mod4"
alt = "mod1"

keys = [
    Key([mod, "shift"], "q", lazy.shutdown()),
    Key([], "XF86PowerOff", lazy.shutdown()),
    Key([mod, "shift"], "r", lazy.restart()),
    Key([mod], "c", lazy.window.kill()),
    Key([mod], "n", lazy.window.toggle_minimize()),
    Key(
        [mod, "shift"],
        "Tab",
        lazy.group.prev_window(),
        lazy.window.disable_floating(),
    ),
    Key([mod], "f", lazy.window.toggle_fullscreen()),
    Key([mod, alt], "j", lazy.window.opacity(0.5)),
    Key([mod, alt], "k", lazy.window.opacity(1.0)),
    Key([mod], "h", lazy.layout.left()),  # Stack  # xmonad-tall
    Key([mod], "l", lazy.layout.right()),  # Stack  # xmonad-tall
    Key([mod], "k", lazy.layout.up()),
    Key([mod], "j", lazy.layout.down()),
    Key(
        [mod, "shift"],
        "l",
        lazy.layout.client_to_next(),  # Stack
        lazy.layout.swap_right(),
        lazy.layout.shuffle_right(),
    ),  # xmonad-tall
    Key(
        [mod, "shift"],
        "h",
        lazy.layout.client_to_previous(),  # Stack
        lazy.layout.swap_left(),
        lazy.layout.shuffle_left(),
    ),  # xmonad-tall
    Key([mod, "shift"], "Return", lazy.layout.toggle_split()),
    Key([mod, "control"], "Return", lazy.layout.swap_main()),
    # Multiple function keys
    Key(
        [mod, "shift"], "space", lazy.layout.rotate(), lazy.layout.flip()
    ),  # xmonad-tall
    Key([mod, "shift"], "k", lazy.layout.shuffle_up()),  # Stack, xmonad-tall
    Key(
        [mod, "shift"], "j", lazy.layout.shuffle_down()
    ),  # Stack, xmonad-tall
    Key([mod, "control"], "m", lazy.layout.maximize()),  # xmonad-tall
    Key([mod, "control"], "n", lazy.layout.normalize()),  # xmonad-tall
    Key(
        [mod, "control"],
        "l",
        lazy.layout.delete(),  # Stack
        lazy.layout.increase_ratio(),  # Tile
        lazy.layout.grow_right(),
    ),  # xmonad-tall
    Key(
        [mod, "control"],
        "h",
        lazy.layout.add(),  # Stack
        lazy.layout.decrease_ratio(),  # Tile
        lazy.layout.shrink(),
        lazy.layout.grow_left(),
    ),  # xmonad-tall
    Key(
        [mod, "control"],
        "k",
        lazy.layout.grow(),  # xmonad-tall
        lazy.layout.decrease_nmaster(),
        lazy.layout.grow_up(),
    ),  # Tile
    Key(
        [mod, "control"],
        "j",
        lazy.layout.shrink(),  # xmonad-tall
        lazy.layout.increase_nmaster(),
        lazy.layout.grow_down(),
    ),  # Tile
    Key([mod], "Tab", lazy.next_layout()),
    # interact with prompts
    Key(["mod4", "shift"], "f", float_to_front),
    Key(
        [mod], "period", lazy.next_screen(), desc="Move focus to next monitor"
    ),
    # start specific apps
    Key([mod], "q", lazy.spawn("firefox")),
    Key([mod], "Return", lazy.spawn("st")),
    # Change the volume if your keyboard has special volume keys.
    Key(
        [mod],
        "space",
        lazy.spawn(
            "rofi -theme-str 'element-icon { size: 2ch;}' -terminal st -show"
        ),
    ),
    Key([mod], "s", lazy.spawn("rofi -terminal st -show ssh")),
    Key([], "XF86AudioRaiseVolume", lazy.spawn("amixer -q  set Master 2dB+")),
    Key([], "XF86AudioLowerVolume", lazy.spawn("amixer -q  set Master 2dB-")),
    Key(
        [],
        "XF86AudioMute",
        lazy.spawn("amixer -q -D pulse sset Master toggle"),
    ),
    Key([], "XF86MonBrightnessUp", lazy.spawn("brightnessctl s 5%+")),
    Key([], "XF86MonBrightnessDown", lazy.spawn("brightnessctl s 5%-")),
    # Also allow changing volume the old fashioned way.
    Key([mod], "equal", lazy.spawn("amixer -c 0 -q set Master 2dB+")),
    Key([mod], "minus", lazy.spawn("amixer -c 0 -q set Master 2dB-")),
    Key(
        ["shift"],
        "Print",
        lazy.spawn(
            'bash -c "maim -d 1 -s | xclip -selection clipboard -t image/png"'
        ),
    ),
    Key(
        [],
        "Print",
        lazy.spawn(
            """bash -c "maim | xclip -selection clipboard -t image/png" """
        ),
    ),
    Key(
        ["control"],
        "Print",
        lazy.spawn(
            'bash -c "maim -B -i $(xdotool getactivewindow) | '
            + "xclip -selection clipboard -t image/png"
        ),
    ),
]

mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod],
        "Button3",
        lazy.window.set_size_floating(),
        start=lazy.window.get_size(),
    ),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]


def get_groups():
    groups = yaml.load(open("/home/droccia/.config/qtile/groups.yaml", "r"))
    g = []
    for counter, group in enumerate(groups["groups"], 1):
        g.append(Group(group["name"], label=group["icon"]))
        keys.append(
            Key([mod], str(counter), lazy.group[group["name"]].toscreen())
        )
        keys.append(
            Key(
                [mod, "shift"],
                str(counter),
                lazy.window.togroup(group["name"]),
            )
        )
    g.append(
        ScratchPad(
            "scratchpad",
            [DropDown("term", "st", opacity=1, height=0.55, width=0.80)],
        )
    )
    keys.extend(
        [
            # Scratchpad
            # toggle visibiliy of above defined DropDown named "term"
            Key([], "F12", lazy.group["scratchpad"].dropdown_toggle("term")),
            Key(
                [], "F11", lazy.group["scratchpad"].dropdown_toggle("qshell")
            ),
        ]
    )
    return g


groups = get_groups()

border = dict(
    border_width=6, margin=10, single_margin=200, border_focus=accent_left
)

layouts = [layout.MonadTall(**border), layout.Columns(**border)]

main = None
follow_mouse_focus = False
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        {"wmclass": "confirm"},
        {"wmclass": "dialog"},
        {"wmclass": "download"},
        {"wmclass": "error"},
        {"wmclass": "file_progress"},
        {"wmclass": "notification"},
        {"wmclass": "splash"},
        {"wmclass": "toolbar"},
        {"wmclass": "confirmreset"},  # gitk
        {"wmclass": "makebranch"},  # gitk
        {"wmclass": "maketag"},  # gitk
        {"wname": "branchdialog"},  # gitk
        {"wname": "pinentry"},  # GPG key password entry
        {"wmclass": "ssh-askpass"},  # ssh-askpass
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"

wmname = "LG3D"


@hook.subscribe.startup_once
def startup():

    import subprocess

    subprocess.Popen(["picom"])
    subprocess.Popen(["systemctl", "--user", "import-environment", "DISPLAY"])
    # subprocess.Popen(["xsettingsd"])
    subprocess.Popen(["nitrogen", "--restore"])
    subprocess.Popen(["unclutter", "--root"])
    subprocess.Popen(["nm-applet"])
    subprocess.Popen(["xautolock", "-time", " 5", "-locker", "screenlock"])
    subprocess.Popen(["dex", "-a", "-s", "/home/droccia/.config/autostart/"])
