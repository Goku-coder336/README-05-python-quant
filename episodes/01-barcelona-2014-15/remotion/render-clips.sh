#!/bin/sh
# Render all 12 Episode 1 clips to ../clips/ (H.264, 1920x1080, 30 fps).
# Usage: sh render-clips.sh            (all clips)
#        sh render-clips.sh C3 C5      (only those)
set -e
cd "$(dirname "$0")"
# Node only uses the session's HTTPS proxy when asked (needed once, for Remotion's browser download)
export NODE_USE_ENV_PROXY=1
[ -f /root/.ccr/ca-bundle.crt ] && export NODE_EXTRA_CA_CERTS=/root/.ccr/ca-bundle.crt

# Re-check the StatsBomb figures against CLAUDE.md and refresh src/data/final.json
python3 ../code/export_remotion_data.py

BUNDLE=$(mktemp -d)/bundle
npx remotion bundle --out-dir="$BUNDLE" >/dev/null

render() { # key composition-id file-name
  case " $ONLY " in *" $1 "*|"  ") ;; *) return 0 ;; esac
  echo "rendering $1 -> clips/$3.mp4"
  npx remotion render "$BUNDLE" "$2" "../clips/$3.mp4" --codec=h264 --crf=18 --log=error
}
ONLY="$*"
render C1a C1a-messi-paradox C1a_messi_paradox
render C1b C1b-scorer-split C1b_scorer_split
render C2 C2-route-intro C2_route_intro
render C2a C2a-route-group-stage C2a_route_group_stage
render C2b C2b-route-r16 C2b_route_r16
render C2c C2c-route-qf C2c_route_qf
render C2d C2d-route-sf C2d_route_sf
render C2e C2e-route-final C2e_route_final
render C2f C2f-route-full C2f_route_full
render C3 C3-final-xg-timeline C3_final_xg_timeline
render C4 C4-final-shot-map C4_final_shot_map
render C5 C5-rakitic-goal-reconstruction C5_rakitic_goal_reconstruction
echo done
