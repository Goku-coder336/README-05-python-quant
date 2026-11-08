import React from "react";
import { Composition, Folder, Still } from "remotion";
import { C1a, C1b } from "./clips/C1";
import { C3, C4, C5 } from "./clips/Final";
import { CFG_C2, CFG_C2A, CFG_C2B, CFG_C2C, CFG_C2D, CFG_C2E, CFG_C2F, Route } from "./clips/Route";
import "./fonts";
import { Thumbnail } from "./Thumbnail";

// Episode 1 (Barcelona 2014/15), Step 5 clips. 1920x1080, 30 fps.
// Each duration is the clip's minimum length from shotlist.md.
export const RemotionRoot: React.FC = () => {
  return (
    <Folder name="Episode1">
      <Composition id="C1a-messi-paradox" component={C1a} durationInFrames={27 * 30} fps={30} width={1920} height={1080} />
      <Composition id="C1b-scorer-split" component={C1b} durationInFrames={39 * 30} fps={30} width={1920} height={1080} />
      <Composition id="C2-route-intro" component={Route} durationInFrames={21 * 30} fps={30} width={1920} height={1080} defaultProps={{ cfg: CFG_C2 }} />
      <Composition id="C2a-route-group-stage" component={Route} durationInFrames={46 * 30} fps={30} width={1920} height={1080} defaultProps={{ cfg: CFG_C2A }} />
      <Composition id="C2b-route-r16" component={Route} durationInFrames={29 * 30} fps={30} width={1920} height={1080} defaultProps={{ cfg: CFG_C2B }} />
      <Composition id="C2c-route-qf" component={Route} durationInFrames={22 * 30} fps={30} width={1920} height={1080} defaultProps={{ cfg: CFG_C2C }} />
      <Composition id="C2d-route-sf" component={Route} durationInFrames={27 * 30} fps={30} width={1920} height={1080} defaultProps={{ cfg: CFG_C2D }} />
      <Composition id="C2e-route-final" component={Route} durationInFrames={8 * 30} fps={30} width={1920} height={1080} defaultProps={{ cfg: CFG_C2E }} />
      <Composition id="C2f-route-full" component={Route} durationInFrames={26 * 30} fps={30} width={1920} height={1080} defaultProps={{ cfg: CFG_C2F }} />
      <Composition id="C3-final-xg-timeline" component={C3} durationInFrames={32 * 30} fps={30} width={1920} height={1080} />
      <Composition id="C4-final-shot-map" component={C4} durationInFrames={12 * 30} fps={30} width={1920} height={1080} />
      <Composition id="C5-rakitic-goal-reconstruction" component={C5} durationInFrames={10 * 30} fps={30} width={1920} height={1080} />
      <Still id="Thumbnail" component={Thumbnail} width={1280} height={720} />
    </Folder>
  );
};
