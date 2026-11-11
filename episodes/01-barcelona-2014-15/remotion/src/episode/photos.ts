// Photos used in the episode, all from Wikimedia Commons under free licences.
// Generated from the Commons metadata; captions say who, where and when (not what the voice is saying).
export const PHOTOS = {
  messi_a: { file: "messi_a.jpg", w: 2400, h: 1600, author: "Ank Kumar", licence: "CC BY-SA 4.0", caption: "Lionel Messi, Camp Nou, September 2014" },
  neymar_b: { file: "neymar_b.jpg", w: 2400, h: 1600, author: "Alex Fau", licence: "CC BY 2.0", caption: "Neymar, February 2015" },
  suarez_super: { file: "suarez_super.jpg", w: 900, h: 655, author: "Oleg Dubyna (Олег Дубина)", licence: "CC BY-SA 3.0", caption: "Luis Suárez, August 2015" },
  iniesta: { file: "iniesta.jpg", w: 599, h: 900, author: "Oleg Dubyna (Олег Дубина)", licence: "CC BY-SA 3.0", caption: "Andrés Iniesta, August 2015" },
} as const;

export type PhotoKey = keyof typeof PHOTOS;
