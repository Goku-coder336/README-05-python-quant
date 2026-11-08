"""Grab one frame from each rendered clip and lay them out on one contact sheet PNG."""
import glob
import os
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

CLIPS = os.path.join(os.path.dirname(__file__), "..", "clips")
ORDER = ["C1a", "C1b", "C2", "C2a", "C2b", "C2c", "C2d", "C2e", "C2f", "C3", "C4", "C5"]
# seconds into each clip for the sample frame (late enough that the main reveals are on screen)
AT = {"C1a": 14, "C1b": 31, "C2": 6, "C2a": 40, "C2b": 24, "C2c": 16, "C2d": 22, "C2e": 6,
      "C2f": 22, "C3": 29, "C4": 10, "C5": 7}


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out)


def main():
    tw, th, pad, lab = 640, 360, 24, 44
    cols, rows = 3, 4
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * pad, rows * (th + lab) + (rows + 1) * pad), "#111110")
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 22)
    small = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Regular.otf", 18)
    tmp = tempfile.mkdtemp()
    for i, key in enumerate(ORDER):
        path = glob.glob(os.path.join(CLIPS, f"{key}_*.mp4"))[0]
        png = os.path.join(tmp, f"{key}.png")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(AT[key]), "-i", path,
                        "-frames:v", "1", png], check=True)
        im = Image.open(png).resize((tw, th), Image.LANCZOS)
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad)
        y = pad + r * (th + lab + pad)
        d.text((x, y + 8), os.path.basename(path), font=font, fill="#f2f0ea")
        d.text((x + tw, y + 12), f"{duration(path):.0f} s · frame at {AT[key]} s", font=small,
               fill="#9a978f", anchor="ra")
        sheet.paste(im, (x, y + lab))
    out = os.path.join(CLIPS, "contact_sheet.png")
    sheet.save(out)
    print(out)


if __name__ == "__main__":
    main()
