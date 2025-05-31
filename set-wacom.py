#!/usr/bin/env python3

import sys
import os
import subprocess
import argparse


def main():
    parser = argparse.ArgumentParser(description="Zooms the Wacom stylus area.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    zoom_parser = subparsers.add_parser(
        "zoom",
        help="Zoom the Wacom stylus area to the bottom right corner of the screen.",
    )
    _ = zoom_parser.add_argument(
        "corner",
        choices=["br", "bl", "tr", "tl"],
        help="The corner to zoom the stylus area to. Options are: br (bottom right), bl (bottom left), tr (top right), tl (top left).",
    )
    _ = zoom_parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the Wacom stylus area to the default before zooming.",
    )
    reset_parser = subparsers.add_parser(
        "reset", help="Reset the Wacom stylus area to the default."
    )
    args = parser.parse_args()

    # run xsetwacom --list devices
    devices = (
        subprocess.check_output(["xsetwacom", "--list", "devices"])
        .decode("utf-8")
        .strip()
        .split("\n")
    )
    # find the ID of the device which contains stylus in its name
    stylus_id = None
    for device in devices:
        if "stylus" in device.lower():
            # the id is shown as id: <digits>
            stylus_id = device.split("id: ")[1].split()[0]
            break
    if stylus_id is None:
        print("No stylus device found.")
        sys.exit(1)

    # handle reset action
    if args.command == "reset" or (args.command == "zoom" and args.reset):
        # reset the stylus area to the default
        print("Resetting stylus area to default.")
        _ = subprocess.run(["xsetwacom", "--set", stylus_id, "resetarea"], check=True)
        print("Stylus area reset successfully.")
        if args.command == "reset":
            return

    # handle zoom action
    # get stylus area
    stylus_area = (
        subprocess.check_output(["xsetwacom", "--get", stylus_id, "area"])
        .decode("utf-8")
        .strip()
    )
    # get x1, y1, x2, y2 from stylus area
    x1, y1, x2, y2 = map(int, stylus_area.split())
    # increase stylus area so that it is only actually handling the given corner of the screen
    width = x2 - x1
    height = y2 - y1

    display_corner = ''
    if args.corner == "br":
        x1 -= width
        y1 -= height
        display_corner = "bottom right"
    elif args.corner == "bl":
        x2 += width
        y1 -= height
        display_corner = "bottom left"
    elif args.corner == "tr":
        x1 -= width
        y2 += height
        display_corner = "top right"
    elif args.corner == "tl":
        x2 += width
        y2 += height
        display_corner = "top left"

    # set stylus area
    print(f"Setting stylus area to {x1}, {y1}, {x2}, {y2} ({display_corner}).")
    _ = subprocess.run(
        ["xsetwacom", "--set", stylus_id, "area", str(x1), str(y1), str(x2), str(y2)],
        check=True,
    )
    print(f"Stylus area set successfully.")


if __name__ == "__main__":
    main()
