"""Test scenes with Pip: the cold open (the case), the pitch scene and the chart. Writes a root that plays them.

Usage: python build/test_pip.py   (from the film folder)
"""
import os

from style import ACCENT, BASE_CSS, INK, MUTED, PIP_JS, TEAM_A, Pitch, defs, pip_svg
from test_stills import FILM, caption, chart_scene, pitch_scene, scene

BLOCK_GREY = "#2a2f38"


def add_pip(html, cid, pid, actions, prefix=None):
    """Put Pip on a full-frame overlay inside a scene and add his moves to its timeline."""
    prefix = prefix or cid
    overlay = (f'<svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0;overflow:visible">'
               f'{defs(prefix + "x")}{pip_svg(pid, prefix + "x")}</svg>')
    html = html.replace('\n  </div>\n  <script>', f'\n    {overlay}\n  </div>\n  <script>', 1)
    html = html.replace(f'    window.__timelines["{cid}"] = tl;', PIP_JS + "\n" + actions + f'\n    window.__timelines["{cid}"] = tl;', 1)
    return html


def open_scene():
    """c0: fifteen blocks, Messi's eight turn red; sixteen blocks, only two do. Pip discovers it."""
    cid = "p-open"
    p = Pitch(180, 20, 13)
    BS, GAP, X0 = 56, 13, 140
    rows = [("GROUP STAGE", 15, 8, 230, 0.6, 1.6), ("KNOCKOUTS", 16, 2, 470, 5.2, 6.6)]
    parts, js = [], []
    for label, total, messi, y, t_drop, t_red in rows:
        r = label[:2].lower()
        parts.append(f'<div id="{cid}-{r}-lbl" class="oswald" style="position:absolute;left:{X0}px;top:{y - 70}px;font-size:40px;color:{MUTED};letter-spacing:.06em;opacity:0">{label}</div>')
        parts.append(f'<div id="{cid}-{r}-num" class="oswald" style="position:absolute;left:{X0 + 16 * (BS + GAP) + 40}px;top:{y - 18}px;font-size:84px;line-height:1;opacity:0">'
                     f'<span style="color:{ACCENT}">{messi}</span><span style="color:{MUTED};font-size:52px"> / {total}</span></div>')
        js.append(f'tl.fromTo("#{cid}-{r}-lbl", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {t_drop - 0.3});')
        for i in range(total):
            bid = f"{cid}-{r}{i}"
            parts.append(f'<div id="{bid}" style="position:absolute;left:{X0 + i * (BS + GAP)}px;top:{y}px;width:{BS}px;height:{BS}px;border-radius:9px;background:{BLOCK_GREY};opacity:0"></div>')
            js.append(f'tl.fromTo("#{bid}", {{ opacity: 0, y: -60 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "bounce.out" }}, {round(t_drop + i * 0.05, 2)});')
            if i < messi:
                tr = round(t_red + i * (0.18 if messi > 2 else 0.5), 2)
                js.append(f'tl.to("#{bid}", {{ backgroundColor: "{TEAM_A}", boxShadow: "0 0 22px {TEAM_A}", duration: 0.15 }}, {tr});')
        js.append(f'tl.fromTo("#{cid}-{r}-num", {{ opacity: 0, scale: 1.25 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "power4.out" }}, {round(t_red + messi * (0.18 if messi > 2 else 0.5) + 0.3, 2)});')
    body = f"""
    <svg width="1920" height="1080" viewBox="0 0 1920 1080" style="position:absolute;inset:0;opacity:.45">{p.svg()}</svg>
    <div style="position:absolute;inset:0;background:radial-gradient(ellipse at 50% 45%, rgba(7,8,10,.2) 0%, rgba(7,8,10,.85) 80%)"></div>
    {''.join(parts)}
    <div class="src" style="left:{X0}px;top:580px">Barcelona's Champions League goals, 2014/15 · Source: UEFA</div>
    {caption(cid, "Barcelona scored sixteen more. Messi scored two.", 5.0, 7.0)}
"""
    html = scene(cid, "", body, "\n    ".join(js))
    # Pip: points at the first row while it turns red, then walks under the second row looking for more
    a = f"""
    Pip.place("{cid}-pip", 1600, 930, 1.7, -1);
    Pip.breathe("{cid}-pip", 0, 4.5);
    Pip.look("{cid}-pip", 6, -7, 0.8);
    Pip.arm("{cid}-pip", "R", -100, 1.3);
    Pip.mood("{cid}-pip", "happy", "smile", 2.9);
    Pip.arm("{cid}-pip", "R", 0, 4.6);
    Pip.mood("{cid}-pip", "normal", "smile", 4.7);
    Pip.walk("{cid}-pip", 1250, 6.3, 1.8);
    Pip.look("{cid}-pip", 7, -8, 6.4);
    Pip.blink("{cid}-pip", 8.8);
    Pip.mood("{cid}-pip", "wide", "o", 9.9);
    Pip.brows("{cid}-pip", -16, 16, 9.95);
    Pip.arm("{cid}-pip", "L", 50, 10.0);
    Pip.arm("{cid}-pip", "R", -50, 10.05);
"""
    return cid, add_pip(html, cid, f"{cid}-pip", a)


def main():
    o_cid, o_html = open_scene()
    p_cid, p_html, p_end = pitch_scene()
    c_cid, c_html = chart_scene()
    # Pip on the touchline of the pitch scene: points at the play, then celebrates the goal
    p_html = add_pip(p_html.replace("t-pitch", "p-pitch"), "p-pitch", "p-pitch-pip", f"""
    Pip.place("p-pitch-pip", 190, 905, 1.35, 1);
    Pip.breathe("p-pitch-pip", 0, 3);
    Pip.arm("p-pitch-pip", "R", -70, 0.8);
    Pip.look("p-pitch-pip", 6, -5, 0.8);
    Pip.mood("p-pitch-pip", "happy", "grin", {round(p_end, 2)});
    Pip.arm("p-pitch-pip", "R", -150, {round(p_end + 0.05, 2)});
    Pip.arm("p-pitch-pip", "L", 150, {round(p_end + 0.1, 2)});
    Pip.jump("p-pitch-pip", {round(p_end + 0.1, 2)});
""")
    c_html = add_pip(c_html.replace("t-chart", "p-chart"), "p-chart", "p-chart-pip", """
    Pip.place("p-chart-pip", 1765, 905, 1.3, -1);
    Pip.breathe("p-chart-pip", 0, 4);
    Pip.look("p-chart-pip", -4, -7, 4.4);
    Pip.arm("p-chart-pip", "R", -105, 4.5);
    Pip.mood("p-chart-pip", "normal", "o", 4.5);
    Pip.brows("p-chart-pip", -10, 10, 4.6);
""")
    durs = {o_cid: 12, "p-pitch": round(p_end + 2.5, 1), "p-chart": 10}
    hosts, start = [], 0.0
    for cid, html in ((o_cid, o_html), ("p-pitch", p_html), ("p-chart", c_html)):
        open(os.path.join(FILM, "compositions", f"{cid}.html"), "w", encoding="utf-8").write(html)
        hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
                     f'data-start="{start}" data-duration="{durs[cid]}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>')
        print(cid, "at", start, "for", durs[cid])
        start += durs[cid]
    for old in ("t-title", "t-pitch", "t-chart"):
        f = os.path.join(FILM, "compositions", f"{old}.html")
        if os.path.exists(f):
            os.remove(f)
    open(os.path.join(FILM, "index.html"), "w", encoding="utf-8").write(f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #07080a; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{start}" data-width="1920" data-height="1080">
{chr(10).join(hosts)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")


if __name__ == "__main__":
    main()
