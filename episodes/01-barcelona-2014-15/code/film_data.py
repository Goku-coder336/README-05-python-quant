"""One data module for the HyperFrames film: every figure on screen comes from here.

Runs the StatsBomb check against CLAUDE.md first, then writes ../film/data/film_data.json:
  run      the verified run (CLAUDE.md, sources: UEFA)
  final    StatsBomb open data for the 2015 final (match 18242): xG series, shots, passes by 15 minutes,
           pressures by third, pass network up to the first substitution, Messi's events, shots created,
           the four goal sequences with the shot freeze frames, substitutions
Usage: python film_data.py
"""
import json
import os

import numpy as np

from c3_final import SHORT, check_figures, load_events, minute_label, shot_table

OUT = os.path.join(os.path.dirname(__file__), "..", "film", "data", "film_data.json")

NAMES = {
    **SHORT,
    "Andrea Barzagli": "Barzagli", "Carlos Alberto Tevez": "Tevez", "Marc-André ter Stegen": "Ter Stegen",
    "Pedro Eliezer Rodríguez Ledesma": "Pedro", "Daniel Alves da Silva": "Dani Alves",
    "Sergio Busquets i Burgos": "Busquets", "Gerard Piqué Bernabéu": "Piqué",
    "Javier Alejandro Mascherano": "Mascherano", "Xavier Hernández Creus": "Xavi",
    "Jérémy Mathieu": "Mathieu", "Andrea Pirlo": "Pirlo", "Claudio Marchisio": "Marchisio",
    "Paul Pogba": "Pogba", "Arturo Erasmo Vidal Pardo": "Vidal", "Leonardo Bonucci": "Bonucci",
    "Patrice Evra": "Evra", "Stephan Lichtsteiner": "Lichtsteiner", "Roberto Maximiliano Pereyra": "Pereyra",
    "Fernando Llorente Torres": "Llorente", "Kingsley Coman": "Coman",
}


def nm(p):
    return NAMES.get(p, p.split()[0])


# Verified run (CLAUDE.md, checked against UEFA's match pages). Barcelona's score first.
RUN = [
    {"round": "Group F", "label": "MD1", "opp": "APOEL", "venue": "H", "res": "W", "score": "1-0", "scorers": [["Piqué", 1]]},
    {"round": "Group F", "label": "MD2", "opp": "PSG", "venue": "A", "res": "L", "score": "2-3", "scorers": [["Messi", 1], ["Neymar", 1]]},
    {"round": "Group F", "label": "MD3", "opp": "Ajax", "venue": "H", "res": "W", "score": "3-1", "scorers": [["Neymar", 1], ["Messi", 1], ["Sandro", 1]]},
    {"round": "Group F", "label": "MD4", "opp": "Ajax", "venue": "A", "res": "W", "score": "2-0", "scorers": [["Messi", 2]]},
    {"round": "Group F", "label": "MD5", "opp": "APOEL", "venue": "A", "res": "W", "score": "4-0", "scorers": [["Messi", 3], ["Suárez", 1]]},
    {"round": "Group F", "label": "MD6", "opp": "PSG", "venue": "H", "res": "W", "score": "3-1", "scorers": [["Messi", 1], ["Neymar", 1], ["Suárez", 1]]},
    {"round": "Round of 16", "label": "Leg 1", "opp": "Man City", "venue": "A", "res": "W", "score": "2-1", "scorers": [["Suárez", 2]]},
    {"round": "Round of 16", "label": "Leg 2", "opp": "Man City", "venue": "H", "res": "W", "score": "1-0", "scorers": [["Rakitić", 1]]},
    {"round": "Quarter-final", "label": "Leg 1", "opp": "PSG", "venue": "A", "res": "W", "score": "3-1", "scorers": [["Neymar", 1], ["Suárez", 2]]},
    {"round": "Quarter-final", "label": "Leg 2", "opp": "PSG", "venue": "H", "res": "W", "score": "2-0", "scorers": [["Neymar", 2]]},
    {"round": "Semi-final", "label": "Leg 1", "opp": "Bayern", "venue": "H", "res": "W", "score": "3-0", "scorers": [["Messi", 2], ["Neymar", 1]]},
    {"round": "Semi-final", "label": "Leg 2", "opp": "Bayern", "venue": "A", "res": "L", "score": "2-3", "scorers": [["Neymar", 2]]},
    {"round": "Final", "label": "Final", "opp": "Juventus", "venue": "N", "res": "W", "score": "3-1", "scorers": [["Rakitić", 1], ["Suárez", 1], ["Neymar", 1]]},
]


def goal_sequence(ev, shot, first_index):
    """Ball path from `first_index` to the shot: passes, carries, shots and saves, as event data gives them."""
    poss = ev[(ev["index"] >= first_index) & (ev["index"] <= shot["index"])]
    steps = []
    for _, r in poss.iterrows():
        t = r.minute * 60 + r.second
        if r.type == "Pass":
            steps.append({"kind": "pass", "player": nm(r.player), "team": r.team, "from": r.location,
                          "to": r.pass_end_location, "to_player": nm(r.pass_recipient) if isinstance(r.pass_recipient, str) else None, "t": int(t)})
        elif r.type == "Carry" and not np.allclose(r.location, r.carry_end_location):
            steps.append({"kind": "carry", "player": nm(r.player), "team": r.team, "from": r.location, "to": r.carry_end_location, "t": int(t)})
        elif r.type == "Dribble":
            steps.append({"kind": "dribble", "player": nm(r.player), "team": r.team, "at": r.location, "t": int(t)})
        elif r.type == "Shot":
            steps.append({"kind": "shot", "player": nm(r.player), "team": r.team, "from": r.location, "to": r.shot_end_location[:2],
                          "outcome": r.shot_outcome, "t": int(t),
                          "freeze": [{"name": nm(p["player"]["name"]), "loc": p["location"], "teammate": p["teammate"]} for p in (r.shot_freeze_frame if isinstance(r.shot_freeze_frame, list) else [])]})
        elif r.type == "Goal Keeper":
            steps.append({"kind": "keeper", "player": nm(r.player), "team": r.team, "at": r.location, "t": int(t)})
        elif r.type == "Dribbled Past":
            steps.append({"kind": "beaten", "player": nm(r.player), "team": r.team, "at": r.location, "t": int(t)})
    return steps


def main():
    ev = load_events()
    totals = check_figures(ev)
    ev = ev.sort_values("index")
    s = shot_table(ev)

    # xG series and shots
    shots = [{"team": r.team, "name": r["name"], "m": round(float(r.m), 3), "x": float(r.x), "y": float(r.y),
              "xg": round(float(r.shot_statsbomb_xg), 4), "goal": r.shot_outcome == "Goal", "label": f"{r['name']} {minute_label(r.m)}"}
             for _, r in s.iterrows()]

    p = ev[ev.type == "Pass"]
    by15 = {t: np.histogram(p[p.team == t].minute, bins=[0, 15, 30, 45, 60, 75, 90, 100])[0].tolist() for t in ("Barcelona", "Juventus")}
    pr = ev[ev.type == "Pressure"]
    thirds = {}
    for t in ("Barcelona", "Juventus"):
        x = np.array([l[0] for l in pr[pr.team == t].location])  # each team attacking left to right
        thirds[t] = [int((x < 40).sum()), int(((x >= 40) & (x < 80)).sum()), int((x >= 80).sum())]

    # pass network: Barcelona completed passes before the first substitution (Iniesta off, 77:17)
    first_sub = ev[(ev.type == "Substitution") & (ev.team == "Barcelona")].iloc[0]
    cut = first_sub.minute * 60 + first_sub.second
    bp = p[(p.team == "Barcelona") & (p.pass_outcome.isna()) & ((p.minute * 60 + p.second) < cut)]
    nodes = {}
    for _, r in bp.iterrows():
        nodes.setdefault(nm(r.player), []).append(r.location)
    links = {}
    for _, r in bp.iterrows():
        k = tuple(sorted([nm(r.player), nm(r.pass_recipient)]))
        links[k] = links.get(k, 0) + 1
    network = {
        "until": f"{first_sub.minute}:{first_sub.second:02d}",
        "passes": int(len(bp)),
        "nodes": [{"name": k, "x": round(float(np.mean([l[0] for l in v])), 1), "y": round(float(np.mean([l[1] for l in v])), 1), "n": len(v)} for k, v in nodes.items()],
        "links": [{"a": a, "b": b, "n": n} for (a, b), n in sorted(links.items(), key=lambda x: -x[1]) if n >= 8],
    }

    # events per Barcelona player, Messi's passes, shots created
    per = ev[ev.team == "Barcelona"].groupby("player").size().sort_values(ascending=False)
    created = p[(p.pass_shot_assist == True) | (p.pass_goal_assist == True)]
    created_b = created[created.team == "Barcelona"].groupby("player").size().sort_values(ascending=False)
    m = ev[ev.player == "Lionel Andrés Messi Cuccittini"]
    assert len(m) == 290 and (m.type == "Pass").sum() == 71 and per.index[0] == "Lionel Andrés Messi Cuccittini"
    assert created_b.index[0] == "Ivan Rakitić" and int(created_b.iloc[0]) == 4

    # the four goals, from the first event the narration names
    # Each goal starts at the first event the narration names (SCRIPT.md 5.2, 5.5, 6.1, 6.4):
    # goal minute -> (player, event type, minute, second) of that first event
    starts = {
        3: ("Lionel Andrés Messi Cuccittini", "Pass", 3, 15),   # Messi switches play to Jordi Alba
        54: ("Andrea Barzagli", "Pass", 54, 14),                # Barzagli finds Tevez
        67: ("Lionel Andrés Messi Cuccittini", "Carry", 67, 46),  # Messi near halfway, carries
        96: ("Neymar da Silva Santos Junior", "Pass", 96, 36),  # Neymar finds Pedro
    }
    goals = {}
    for _, g in ev[(ev.type == "Shot") & (ev.shot_outcome == "Goal")].iterrows():
        player, typ, mi, se = starts[g.minute]
        hit = ev[(ev.player == player) & (ev.type == typ) & (ev.minute == mi) & (ev.second == se)]
        assert len(hit) == 1, (g.minute, len(hit))
        goals[minute_label(g.minute + g.second / 60)] = goal_sequence(ev, g, int(hit.iloc[0]["index"]))

    subs = [{"t": f"{r.minute}:{r.second:02d}", "team": r.team, "off": nm(r.player), "on": nm(r.substitution_replacement)}
            for _, r in ev[ev.type == "Substitution"].iterrows()]

    data = {
        "source_final": "StatsBomb open data, match 18242 (Juventus 1-3 Barcelona, 6 June 2015)",
        "run": RUN,
        "totals": {f"{k[0]}_{k[1]}": v for k, v in totals.items()},
        "shots": shots,
        "passes_by_15": by15,
        "pressures_by_third": thirds,
        "network": network,
        "events_per_player": {nm(k): int(v) for k, v in per.head(4).items()},
        "messi": {"events": int(len(m)), "passes": int((m.type == "Pass").sum())},
        "shots_created": {nm(k): int(v) for k, v in created_b.items()},
        "goals": goals,
        "subs": subs,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("wrote", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
