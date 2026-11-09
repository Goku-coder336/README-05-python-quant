#!/bin/sh
# Render the finished Episode 1 video (voiceover, clips, cards, charts) to ../publish/.
# Run ../code/voiceover.py first if the script or the voice changed.
set -e
cd "$(dirname "$0")"
export NODE_USE_ENV_PROXY=1
[ -f /root/.ccr/ca-bundle.crt ] && export NODE_EXTRA_CA_CERTS=/root/.ccr/ca-bundle.crt
python3 ../code/export_remotion_data.py
npx remotion render Episode1-full ../publish/episode1_barcelona_2014-15.mp4 \
  --codec=h264 --crf=18 --audio-codec=aac --audio-bitrate=192k --log=error
echo done
