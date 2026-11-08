import { loadFont } from "@remotion/fonts";
import { staticFile } from "remotion";

// Inter, bundled from public/fonts so renders never depend on a font download.
export const fontsReady = Promise.all([
  loadFont({ family: "Inter", url: staticFile("fonts/Inter-Regular.otf"), weight: "400" }),
  loadFont({ family: "Inter", url: staticFile("fonts/Inter-SemiBold.otf"), weight: "600" }),
  loadFont({ family: "Inter", url: staticFile("fonts/Inter-Bold.otf"), weight: "700" }),
]);
