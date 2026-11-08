"""Export the 2015 final's StatsBomb data for the Remotion clips (C3, C4, C5).

Checks the figures against CLAUDE.md first and stops if anything differs.
Writes ../remotion/src/data/final.json.
"""
import json
import os

import numpy as np

from c3_final import SHORT, check_figures, load_events, minute_label, shot_table

OUT = os.path.join(os.path.dirname(__file__), "..", "remotion", "src", "data", "final.json")


def main():
    ev = load_events()
    totals = check_figures(ev)
    s = shot_table(ev)
    shots = [
        {"team": r.team, "name": r["name"], "m": round(float(r.m), 3), "x": float(r.x), "y": float(r.y),
         "xg": round(float(r.shot_statsbomb_xg), 4), "goal": r.shot_outcome == "Goal",
         "label": f"{r['name']} {minute_label(r.m)}"}
        for _, r in s.iterrows()
    ]

    # Rakitić's 4th-minute goal: from Messi's carry (event index 135) to the shot
    ev = ev.sort_values("index")
    shot = ev[(ev.type == "Shot") & (ev.shot_outcome == "Goal") & (ev.period == 1)].iloc[0]
    assert SHORT[shot.player] == "Rakitić" and shot.minute == 3
    poss = ev[(ev.possession == shot.possession) & (ev["index"] >= 135) & (ev["index"] <= shot["index"])]
    segs = []
    for _, r in poss.iterrows():
        if r.type == "Carry" and not np.allclose(r.location, r.carry_end_location):
            segs.append({"kind": "carry", "player": SHORT[r.player], "from": r.location,
                         "to": r.carry_end_location})
        elif r.type == "Pass":
            segs.append({"kind": "pass", "player": SHORT[r.player], "from": r.location,
                         "to": r.pass_end_location, "to_player": SHORT[r.pass_recipient]})
    segs[-1]["to"] = shot.location  # the last pass ends where the shot was taken
    segs.append({"kind": "shot", "player": "Rakitić", "from": shot.location,
                 "to": shot.shot_end_location[:2]})
    freeze = [{"name": SHORT.get(p["player"]["name"], p["player"]["name"]), "loc": p["location"],
               "teammate": p["teammate"]} for p in shot.shot_freeze_frame]

    data = {
        "source": "StatsBomb open data, match 18242 (Juventus 1-3 Barcelona, 6 June 2015)",
        "totals": {f"{k[0]}_{k[1]}": v for k, v in totals.items()},
        "shots": shots,
        "rakitic": {"segments": segs, "freeze": freeze},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("wrote", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
