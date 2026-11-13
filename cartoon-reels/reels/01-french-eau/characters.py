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
