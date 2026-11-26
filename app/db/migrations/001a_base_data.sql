-- Reference data later migrations point at, so a fresh database migrates fully before seeding.
-- Same rows as src/lib/seed.ts; existing rows are left alone.
insert into traditions (id, slug, name) values
  ('t-kh','kerala-hindu','Kerala Hindu'),
  ('t-kc','kerala-christian','Kerala Christian'),
  ('t-km','kerala-muslim','Kerala Muslim'),
  ('t-ta','tamil','Tamil'),
  ('t-any','any','Any or mixed')
on conflict (id) do nothing;
insert into categories (id, slug, name, kind, icon) values
  ('k-plan','event-planners','Event planners','service','ClipboardText'),
  ('k-mua','makeup','Makeup artists','service','PaintBrush'),
  ('k-photo','photography','Photographers','service','Camera'),
  ('k-video','videography','Videographers','service','VideoCamera'),
  ('k-decor','decor','Decor','service','FlowerLotus'),
  ('k-cater','catering','Catering','service','CookingPot'),
  ('k-sound','sound','Sound rental','equipment','SpeakerHifi'),
  ('k-light','lighting','Lighting rental','equipment','Lightbulb'),
  ('k-power','generators','Generators','equipment','Lightning')
on conflict (id) do nothing;
