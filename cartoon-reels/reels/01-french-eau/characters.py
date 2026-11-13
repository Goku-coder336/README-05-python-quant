"""Series characters drawn as SVG, rigged in separate parts.

Both characters are original designs for the Word Song series.
Every part is its own <g> with an id `<prefix>-<part>` so GSAP can move it:
  head, brow-l, brow-r, eye-l, eye-r, mouth-c (closed), mouth-o (open),
  body, arm-l, arm-r, legs.
Pivots (SVG user units, pass to GSAP as svgOrigin) are listed in PIVOTS.
"""

INK = "#1d1d1b"
OUT = 6  # outline width

# ---------------------------------------------------------------- teacher ----
# Barnaby: tall curl of hair, big round glasses, mustard cardigan, teal bow tie,
# carries a wooden pointer. viewBox 0 0 600 900.
TEACHER_SKIN = "#f3cfa8"
MUSTARD = "#e8b13c"
TEAL = "#2fa39a"
HAIR_BROWN = "#3b2a20"

TEACHER_PIVOTS = {
    "head": "300 415",
    "arm-l": "205 455",
    "arm-r": "395 455",
    "body": "300 700",
    "brow-l": "248 178",
    "brow-r": "352 178",
    "eye-l": "252 252",
    "eye-r": "348 252",
}


def limb(x1, y1, x2, y2, colour, width=40):
    """A noodle limb: dark outline stroke under a coloured stroke."""
    d = f"M{x1} {y1} L{x2} {y2}"
    return (
        f'<path d="{d}" stroke="{INK}" stroke-width="{width + 2 * OUT}" stroke-linecap="round" fill="none"/>'
        f'<path d="{d}" stroke="{colour}" stroke-width="{width}" stroke-linecap="round" fill="none"/>'
    )


def teacher(p):
    o = f'stroke="{INK}" stroke-width="{OUT}" stroke-linejoin="round"'
    return f"""
<svg id="{p}" viewBox="0 0 600 900" xmlns="http://www.w3.org/2000/svg" overflow="visible">
  <g id="{p}-legs">
    <rect x="245" y="680" width="44" height="150" rx="16" fill="#3a3f55" {o}/>
    <rect x="311" y="680" width="44" height="150" rx="16" fill="#3a3f55" {o}/>
    <ellipse cx="258" cy="840" rx="42" ry="20" fill="#6b4a32" {o}/>
    <ellipse cx="342" cy="840" rx="42" ry="20" fill="#6b4a32" {o}/>
  </g>
  <g id="{p}-arm-l">
    {limb(205, 455, 168, 600, MUSTARD)}
    <circle cx="166" cy="606" r="24" fill="{TEACHER_SKIN}" {o}/>
  </g>
  <g id="{p}-body">
    <path d="M200 430 Q300 405 400 430 L440 700 Q300 722 160 700 Z" fill="{MUSTARD}" {o}/>
    <path d="M265 432 L300 482 L335 432 Z" fill="#fffdf6" {o}/>
    <path d="M300 482 L300 708" stroke="{INK}" stroke-width="4" fill="none"/>
    <circle cx="318" cy="530" r="7" fill="#8a5a1c"/>
    <circle cx="318" cy="590" r="7" fill="#8a5a1c"/>
    <circle cx="318" cy="650" r="7" fill="#8a5a1c"/>
    <path d="M300 452 L262 432 L262 474 Z" fill="{TEAL}" {o}/>
    <path d="M300 452 L338 432 L338 474 Z" fill="{TEAL}" {o}/>
    <circle cx="300" cy="452" r="10" fill="{TEAL}" {o}/>
  </g>
  <g id="{p}-head">
    <rect x="275" y="385" width="50" height="45" fill="{TEACHER_SKIN}" {o}/>
    <circle cx="188" cy="262" r="26" fill="{TEACHER_SKIN}" {o}/>
    <circle cx="412" cy="262" r="26" fill="{TEACHER_SKIN}" {o}/>
    <rect x="190" y="110" width="220" height="300" rx="100" fill="{TEACHER_SKIN}" {o}/>
    <path d="M262 124 C246 58 282 6 326 16 C366 26 364 84 332 86 C310 88 302 64 318 54 C298 52 286 84 300 122 Z" fill="{HAIR_BROWN}" {o}/>
    <path d="M196 196 Q200 150 232 132 Q214 170 214 204 Z" fill="{HAIR_BROWN}" {o}/>
    <path d="M404 196 Q400 150 368 132 Q386 170 386 204 Z" fill="{HAIR_BROWN}" {o}/>
    <g id="{p}-brow-l"><path d="M218 178 L282 174" stroke="{INK}" stroke-width="13" stroke-linecap="round"/></g>
    <g id="{p}-brow-r"><path d="M318 174 L382 178" stroke="{INK}" stroke-width="13" stroke-linecap="round"/></g>
    <path d="M206 240 L190 252 M394 240 L410 252" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>
    <circle cx="252" cy="248" r="46" fill="#fffdf6" stroke="{INK}" stroke-width="7"/>
    <circle cx="348" cy="248" r="46" fill="#fffdf6" stroke="{INK}" stroke-width="7"/>
    <path d="M296 242 Q300 236 304 242" stroke="{INK}" stroke-width="6" fill="none" stroke-linecap="round"/>
    <g id="{p}-eye-l"><circle cx="252" cy="252" r="13" fill="{INK}"/></g>
    <g id="{p}-eye-r"><circle cx="348" cy="252" r="13" fill="{INK}"/></g>
    <path d="M300 276 Q320 304 297 312" stroke="{INK}" stroke-width="6" fill="none" stroke-linecap="round"/>
    <g id="{p}-mouth-c"><path d="M272 352 L328 352" stroke="{INK}" stroke-width="7" stroke-linecap="round"/></g>
    <g id="{p}-mouth-o" opacity="0">
      <ellipse cx="300" cy="354" rx="26" ry="19" fill="#5a1e1e" {o}/>
      <ellipse cx="300" cy="362" rx="13" ry="6" fill="#e86a6a"/>
    </g>
  </g>
  <g id="{p}-arm-r">
    <path d="M436 606 L470 770" stroke="{INK}" stroke-width="20" stroke-linecap="round"/>
    <path d="M436 606 L470 770" stroke="#a8743f" stroke-width="10" stroke-linecap="round"/>
    <circle cx="471" cy="772" r="7" fill="#fffdf6" stroke="{INK}" stroke-width="4"/>
    {limb(395, 455, 432, 600, MUSTARD)}
    <circle cx="434" cy="606" r="24" fill="{TEACHER_SKIN}" {o}/>
  </g>
</svg>"""


# ---------------------------------------------------------------- partner ----
# Odette: big black hair bun, coral top, yellow hoop earrings and trainers.
# viewBox 0 0 500 820.
PARTNER_SKIN = "#c98b5e"
CORAL = "#ff6f61"
HAIR_DARK = "#2b2233"
YELLOW = "#ffd23f"

PARTNER_PIVOTS = {
    "head": "250 385",
    "arm-l": "165 440",
    "arm-r": "335 440",
    "body": "250 640",
    "brow-l": "204 202",
    "brow-r": "296 202",
    "eye-l": "205 252",
    "eye-r": "295 252",
}


def partner(p):
    o = f'stroke="{INK}" stroke-width="{OUT}" stroke-linejoin="round"'
    return f"""
<svg id="{p}" viewBox="0 0 500 820" xmlns="http://www.w3.org/2000/svg" overflow="visible">
  <g id="{p}-legs">
    <rect x="200" y="600" width="38" height="150" rx="15" fill="{HAIR_DARK}" {o}/>
    <rect x="262" y="600" width="38" height="150" rx="15" fill="{HAIR_DARK}" {o}/>
    <ellipse cx="212" cy="762" rx="40" ry="20" fill="{YELLOW}" {o}/>
    <ellipse cx="288" cy="762" rx="40" ry="20" fill="{YELLOW}" {o}/>
  </g>
  <g id="{p}-arm-l">
    {limb(165, 440, 100, 560, CORAL, 38)}
    <circle cx="97" cy="566" r="22" fill="{PARTNER_SKIN}" {o}/>
  </g>
  <g id="{p}-arm-r">
    {limb(335, 440, 400, 560, CORAL, 38)}
    <circle cx="403" cy="566" r="22" fill="{PARTNER_SKIN}" {o}/>
  </g>
  <g id="{p}-body">
    <path d="M175 405 Q250 378 325 405 Q392 520 360 625 Q250 655 140 625 Q108 520 175 405 Z" fill="{CORAL}" {o}/>
    <path d="M205 402 Q250 440 295 402" fill="#fffdf6" {o}/>
    <path d="M150 560 Q250 590 350 560" stroke="{INK}" stroke-width="5" fill="none"/>
  </g>
  <g id="{p}-head">
    <rect x="228" y="360" width="44" height="45" fill="{PARTNER_SKIN}" {o}/>
    <circle cx="250" cy="96" r="70" fill="{HAIR_DARK}" {o}/>
    <circle cx="250" cy="252" r="125" fill="{PARTNER_SKIN}" {o}/>
    <path d="M128 236 Q144 122 250 118 Q356 122 372 236 Q332 172 250 178 Q168 172 128 236 Z" fill="{HAIR_DARK}" {o}/>
    <circle cx="126" cy="304" r="17" fill="none" stroke="{YELLOW}" stroke-width="8"/>
    <circle cx="374" cy="304" r="17" fill="none" stroke="{YELLOW}" stroke-width="8"/>
    <g id="{p}-brow-l"><path d="M180 208 Q204 192 228 202" stroke="{INK}" stroke-width="10" fill="none" stroke-linecap="round"/></g>
    <g id="{p}-brow-r"><path d="M272 202 Q296 192 320 208" stroke="{INK}" stroke-width="10" fill="none" stroke-linecap="round"/></g>
    <ellipse cx="205" cy="252" rx="25" ry="31" fill="#fffdf6" stroke="{INK}" stroke-width="5"/>
    <ellipse cx="295" cy="252" rx="25" ry="31" fill="#fffdf6" stroke="{INK}" stroke-width="5"/>
    <g id="{p}-eye-l"><circle cx="209" cy="258" r="12" fill="{INK}"/></g>
    <g id="{p}-eye-r"><circle cx="291" cy="258" r="12" fill="{INK}"/></g>
    <circle cx="176" cy="304" r="16" fill="#ff8f8f" opacity="0.7"/>
    <circle cx="324" cy="304" r="16" fill="#ff8f8f" opacity="0.7"/>
    <path d="M250 276 Q262 292 248 298" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>
    <g id="{p}-mouth-c"><path d="M222 322 Q250 342 278 322" stroke="{INK}" stroke-width="7" fill="none" stroke-linecap="round"/></g>
    <g id="{p}-mouth-o" opacity="0">
      <path d="M214 314 Q250 380 286 314 Z" fill="#5a1e1e" {o}/>
      <ellipse cx="250" cy="346" rx="14" ry="7" fill="#e86a6a"/>
    </g>
  </g>
</svg>"""


# ------------------------------------------------- teacher option B: pigeon ---
# Gilbert: grey pigeon, red knitted scarf, orange eyes, iridescent neck band.
# Same viewBox, part ids and pivots as the human teacher (TEACHER_PIVOTS).
PIGEON = "#a3acbf"
PIGEON_DARK = "#7c869b"
SCARF = "#d9382f"


def teacher_pigeon(p):
    o = f'stroke="{INK}" stroke-width="{OUT}" stroke-linejoin="round"'
    return f"""
<svg id="{p}" viewBox="0 0 600 900" xmlns="http://www.w3.org/2000/svg" overflow="visible">
  <g id="{p}-legs">
    <path d="M262 700 L262 820 M338 700 L338 820" stroke="{INK}" stroke-width="22" stroke-linecap="round"/>
    <path d="M262 700 L262 820 M338 700 L338 820" stroke="#e5815a" stroke-width="10" stroke-linecap="round"/>
    <path d="M226 836 L262 818 L298 836 M262 818 L262 842 M302 836 L338 818 L374 836 M338 818 L338 842" stroke="{INK}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    <path d="M226 836 L262 818 L298 836 M262 818 L262 842 M302 836 L338 818 L374 836 M338 818 L338 842" stroke="#e5815a" stroke-width="9" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
  </g>
  <g id="{p}-arm-l">
    <path d="M205 455 Q120 520 150 640 Q200 600 230 520 Z" fill="{PIGEON_DARK}" {o}/>
    <path d="M165 600 L150 640 M185 595 L172 632" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>
  </g>
  <g id="{p}-body">
    <ellipse cx="300" cy="555" rx="165" ry="185" fill="{PIGEON}" {o}/>
    <ellipse cx="300" cy="600" rx="105" ry="125" fill="#c3cad8"/>
    <path d="M250 640 Q300 660 350 640 M260 690 Q300 706 340 690" stroke="{PIGEON_DARK}" stroke-width="5" fill="none" stroke-linecap="round"/>
  </g>
  <g id="{p}-head">
    <path d="M222 380 Q300 420 378 380 L372 420 Q300 455 228 420 Z" fill="#5fae9a" {o}/>
    <path d="M232 396 Q300 430 368 396" stroke="#8d6bb8" stroke-width="10" fill="none"/>
    <path d="M200 412 Q300 470 400 412 L404 452 Q300 505 196 452 Z" fill="{SCARF}" {o}/>
    <path d="M330 470 L346 610 L384 600 L362 462 Z" fill="{SCARF}" {o}/>
    <path d="M348 612 L344 636 M362 610 L362 634 M376 606 L380 630" stroke="{SCARF}" stroke-width="8" stroke-linecap="round"/>
    <path d="M220 430 L230 444 M250 440 L258 456 M280 446 L286 462 M320 446 L314 462 M350 440 L342 456 M380 430 L370 444" stroke="#a5261f" stroke-width="5" stroke-linecap="round"/>
    <circle cx="300" cy="255" r="135" fill="{PIGEON}" {o}/>
    <path d="M262 126 Q280 92 300 120 Q318 90 340 126" fill="{PIGEON_DARK}" {o}/>
    <g id="{p}-brow-l"><path d="M214 182 L282 176" stroke="{INK}" stroke-width="12" stroke-linecap="round"/></g>
    <g id="{p}-brow-r"><path d="M318 176 L386 182" stroke="{INK}" stroke-width="12" stroke-linecap="round"/></g>
    <circle cx="252" cy="248" r="40" fill="#f29a3a" stroke="{INK}" stroke-width="6"/>
    <circle cx="348" cy="248" r="40" fill="#f29a3a" stroke="{INK}" stroke-width="6"/>
    <g id="{p}-eye-l"><circle cx="252" cy="252" r="18" fill="{INK}"/><circle cx="246" cy="244" r="5" fill="#fff"/></g>
    <g id="{p}-eye-r"><circle cx="348" cy="252" r="18" fill="{INK}"/><circle cx="342" cy="244" r="5" fill="#fff"/></g>
    <ellipse cx="300" cy="300" rx="22" ry="12" fill="#eef0f5" {o}/>
    <g id="{p}-mouth-c"><path d="M272 312 L300 356 L328 312 Z" fill="#4b4f5c" {o}/></g>
    <g id="{p}-mouth-o" opacity="0">
      <path d="M268 306 L300 330 L332 306 Z" fill="#4b4f5c" {o}/>
      <path d="M276 340 L300 372 L324 340 Z" fill="#4b4f5c" {o}/>
      <path d="M282 326 L318 326 L310 342 L290 342 Z" fill="#5a1e1e"/>
    </g>
  </g>
  <g id="{p}-arm-r">
    <path d="M436 600 L470 770" stroke="{INK}" stroke-width="20" stroke-linecap="round"/>
    <path d="M436 600 L470 770" stroke="#a8743f" stroke-width="10" stroke-linecap="round"/>
    <circle cx="471" cy="772" r="7" fill="#fffdf6" stroke="{INK}" stroke-width="4"/>
    <path d="M395 455 Q480 520 450 640 Q400 600 370 520 Z" fill="{PIGEON_DARK}" {o}/>
    <path d="M435 600 L450 640 M415 595 L428 632" stroke="{INK}" stroke-width="5" stroke-linecap="round"/>
  </g>
</svg>"""


# -------------------------------------------------- teacher option C: robot ---
# Unit 7: boxy robot, antenna with a red bulb, screen face. Same rig as above.
STEEL = "#8fb3c9"
STEEL_DARK = "#5d7f96"
SCREEN = "#20323f"
GLOW = "#7ff0d0"


def teacher_robot(p):
    o = f'stroke="{INK}" stroke-width="{OUT}" stroke-linejoin="round"'
    return f"""
<svg id="{p}" viewBox="0 0 600 900" xmlns="http://www.w3.org/2000/svg" overflow="visible">
  <g id="{p}-legs">
    <rect x="240" y="690" width="46" height="130" rx="8" fill="{STEEL_DARK}" {o}/>
    <rect x="314" y="690" width="46" height="130" rx="8" fill="{STEEL_DARK}" {o}/>
    <rect x="216" y="816" width="84" height="32" rx="10" fill="#3a3f55" {o}/>
    <rect x="300" y="816" width="84" height="32" rx="10" fill="#3a3f55" {o}/>
  </g>
  <g id="{p}-arm-l">
    {limb(205, 455, 168, 600, STEEL_DARK, 32)}
    <path d="M150 600 L150 632 L166 620 L182 632 L182 600 Z" fill="{STEEL}" {o}/>
  </g>
  <g id="{p}-body">
    <rect x="185" y="425" width="230" height="280" rx="26" fill="{STEEL}" {o}/>
    <rect x="225" y="470" width="150" height="110" rx="14" fill="{SCREEN}" {o}/>
    <rect x="245" y="495" width="30" height="14" rx="4" fill="#ff5a4e"/>
    <rect x="285" y="495" width="30" height="14" rx="4" fill="{GLOW}"/>
    <rect x="325" y="495" width="30" height="14" rx="4" fill="#ffd23f"/>
    <path d="M245 540 L355 540" stroke="{GLOW}" stroke-width="6" stroke-linecap="round"/>
    <circle cx="225" cy="650" r="10" fill="{STEEL_DARK}"/><circle cx="375" cy="650" r="10" fill="{STEEL_DARK}"/>
  </g>
  <g id="{p}-head">
    <rect x="280" y="385" width="40" height="45" fill="{STEEL_DARK}" {o}/>
    <path d="M300 130 L300 60" stroke="{INK}" stroke-width="8"/>
    <circle cx="300" cy="48" r="22" fill="#ff5a4e" {o}/>
    <circle cx="293" cy="41" r="6" fill="#ffb3ad"/>
    <rect x="170" y="210" width="34" height="90" rx="10" fill="{STEEL_DARK}" {o}/>
    <rect x="396" y="210" width="34" height="90" rx="10" fill="{STEEL_DARK}" {o}/>
    <rect x="195" y="125" width="210" height="270" rx="36" fill="{STEEL}" {o}/>
    <rect x="215" y="160" width="170" height="210" rx="22" fill="{SCREEN}" {o}/>
    <g id="{p}-brow-l"><path d="M228 192 L280 188" stroke="{GLOW}" stroke-width="10" stroke-linecap="round"/></g>
    <g id="{p}-brow-r"><path d="M320 188 L372 192" stroke="{GLOW}" stroke-width="10" stroke-linecap="round"/></g>
    <g id="{p}-eye-l"><rect x="232" y="228" width="40" height="48" rx="8" fill="{GLOW}"/></g>
    <g id="{p}-eye-r"><rect x="328" y="228" width="40" height="48" rx="8" fill="{GLOW}"/></g>
    <g id="{p}-mouth-c"><path d="M262 330 L338 330" stroke="{GLOW}" stroke-width="8" stroke-linecap="round"/></g>
    <g id="{p}-mouth-o" opacity="0">
      <rect x="258" y="310" width="84" height="40" rx="8" fill="none" stroke="{GLOW}" stroke-width="7"/>
      <path d="M279 312 L279 348 M300 312 L300 348 M321 312 L321 348" stroke="{GLOW}" stroke-width="5"/>
    </g>
  </g>
  <g id="{p}-arm-r">
    <path d="M436 606 L470 770" stroke="{INK}" stroke-width="20" stroke-linecap="round"/>
    <path d="M436 606 L470 770" stroke="#a8743f" stroke-width="10" stroke-linecap="round"/>
    <circle cx="471" cy="772" r="7" fill="#fffdf6" stroke="{INK}" stroke-width="4"/>
    {limb(395, 455, 432, 600, STEEL_DARK, 32)}
    <path d="M418 600 L418 632 L434 620 L450 632 L450 600 Z" fill="{STEEL}" {o}/>
  </g>
</svg>"""


TEACHERS = {"A": teacher, "B": teacher_pigeon, "C": teacher_robot}
