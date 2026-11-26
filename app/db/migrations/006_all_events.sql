-- Any kind of event: grouped event types, more vendor categories, more traditions, and a checklist for every type.

alter table event_types add column grp text not null default 'Celebrations';
alter table event_types add column description text not null default '';
alter table event_types add column active boolean not null default true;
update event_types set grp = 'Weddings and family' where id in ('et-wedding','et-engage','et-proposal');
update event_types set grp = 'Religious and cultural' where id = 'et-baptism';
update event_types set grp = 'Parties and celebrations' where id = 'et-birthday';
update event_types set grp = 'Business and professional' where id = 'et-corporate';
alter table traditions add column active boolean not null default true;
alter table categories add column active boolean not null default true;

-- Vendor categories needed beyond weddings
insert into categories (id, slug, name, kind, icon) values
  ('k-venue',    'venues', 'Venues and halls', 'service', 'Buildings'),
  ('k-priest',   'priests-officiants', 'Priests and officiants', 'service', 'HandsPraying'),
  ('k-florist',  'florists', 'Florists', 'service', 'Flower'),
  ('k-print',    'invitations-printing', 'Invitations and printing', 'service', 'Envelope'),
  ('k-gifts',    'gifts-favours', 'Gifts and favours', 'service', 'Gift'),
  ('k-kids',     'kids-entertainment', 'Kids entertainment', 'service', 'Balloon'),
  ('k-security', 'security-staff', 'Security and crowd staff', 'service', 'ShieldCheck'),
  ('k-hosts',    'hosts-ushers', 'Hosts, ushers and helpers', 'service', 'UsersThree'),
  ('k-clean',    'cleaning', 'Cleaning', 'service', 'Broom'),
  ('k-brand',    'branding-signage', 'Branding and signage', 'service', 'Flag'),
  ('k-stream',   'live-streaming', 'Live streaming', 'service', 'Broadcast'),
  ('k-av',       'av-led-screens', 'Projectors and LED screens', 'equipment', 'Monitor'),
  ('k-stage',    'stage-truss', 'Stage and truss', 'equipment', 'Cube'),
  ('k-tent',     'tents-canopies', 'Tents and canopies', 'equipment', 'Tent'),
  ('k-furn',     'furniture-rental', 'Furniture rental', 'equipment', 'Armchair'),
  ('k-cool',     'fans-coolers', 'Fans, coolers and AC', 'equipment', 'Fan')
on conflict (id) do nothing;

-- More traditions (used to suggest, never to restrict)
insert into traditions (id, slug, name) values
  ('t-hn',  'north-indian-hindu', 'North Indian Hindu'),
  ('t-sik', 'sikh', 'Sikh'),
  ('t-chr', 'christian', 'Christian (general)'),
  ('t-mus', 'muslim', 'Muslim (general)'),
  ('t-tb',  'tamil-brahmin', 'Tamil Brahmin'),
  ('t-sec', 'secular', 'Non-religious')
on conflict (id) do nothing;

-- Event types across every part of life
insert into event_types (id, slug, name, icon, sort, grp) values
  ('et-reception',   'reception', 'Wedding reception', 'Champagne', 7, 'Weddings and family'),
  ('et-anniv',       'anniversary', 'Anniversary', 'Heart', 8, 'Weddings and family'),
  ('et-babyshower',  'baby-shower', 'Baby shower', 'Baby', 9, 'Weddings and family'),
  ('et-naming',      'naming-ceremony', 'Naming ceremony', 'Baby', 10, 'Weddings and family'),
  ('et-housewarm',   'housewarming', 'Housewarming', 'House', 11, 'Weddings and family'),
  ('et-retire',      'retirement', 'Retirement party', 'Coffee', 12, 'Weddings and family'),
  ('et-memorial',    'memorial', 'Memorial or remembrance', 'Flower', 13, 'Weddings and family'),
  ('et-communion',   'first-communion', 'First Holy Communion', 'Church', 20, 'Religious and cultural'),
  ('et-puja',        'puja', 'Puja or homam', 'FlowerLotus', 21, 'Religious and cultural'),
  ('et-iftar',       'iftar', 'Iftar or Eid gathering', 'MoonStars', 22, 'Religious and cultural'),
  ('et-festival',    'festival', 'Festival celebration (Onam, Diwali, Christmas)', 'Sparkle', 23, 'Religious and cultural'),
  ('et-temple',      'temple-church-feast', 'Temple, church or mosque event', 'Bank', 24, 'Religious and cultural'),
  ('et-kids',        'kids-party', 'Kids party', 'Balloon', 30, 'Parties and celebrations'),
  ('et-reunion',     'reunion', 'Reunion', 'UsersThree', 31, 'Parties and celebrations'),
  ('et-dinner',      'private-dinner', 'Private dinner', 'ForkKnife', 32, 'Parties and celebrations'),
  ('et-newyear',     'new-year-party', 'New Year or theme party', 'Confetti', 33, 'Parties and celebrations'),
  ('et-conf',        'conference', 'Conference or seminar', 'Presentation', 40, 'Business and professional'),
  ('et-launch',      'product-launch', 'Product launch', 'RocketLaunch', 41, 'Business and professional'),
  ('et-expo',        'exhibition', 'Exhibition or trade show', 'Storefront', 42, 'Business and professional'),
  ('et-offsite',     'team-offsite', 'Team outing or offsite', 'Mountains', 43, 'Business and professional'),
  ('et-awards',      'awards-night', 'Awards night or gala', 'Trophy', 44, 'Business and professional'),
  ('et-opening',     'shop-opening', 'Shop or office opening', 'Storefront', 45, 'Business and professional'),
  ('et-college',     'college-fest', 'College or school event', 'GraduationCap', 50, 'Community and public'),
  ('et-sports',      'sports-event', 'Sports event or tournament', 'SoccerBall', 51, 'Community and public'),
  ('et-concert',     'concert', 'Concert or live show', 'MusicNotes', 52, 'Community and public'),
  ('et-charity',     'charity', 'Charity or fundraiser', 'HandHeart', 53, 'Community and public'),
  ('et-community',   'community-gathering', 'Community or association meeting', 'UsersThree', 54, 'Community and public'),
  ('et-other',       'other', 'Something else', 'Sparkle', 99, 'Something else')
on conflict (id) do nothing;

insert into event_templates (id, event_type_id, tradition_id, size_tier) values
  ('tp-reception','et-reception',null,'standard'), ('tp-anniv','et-anniv',null,'standard'), ('tp-babyshower','et-babyshower',null,'standard'),
  ('tp-naming','et-naming',null,'standard'), ('tp-housewarm','et-housewarm',null,'standard'), ('tp-retire','et-retire',null,'standard'),
  ('tp-memorial','et-memorial',null,'standard'), ('tp-communion','et-communion',null,'standard'), ('tp-puja','et-puja',null,'standard'),
  ('tp-iftar','et-iftar',null,'standard'), ('tp-festival','et-festival',null,'standard'), ('tp-temple','et-temple',null,'standard'),
  ('tp-kids','et-kids',null,'standard'), ('tp-reunion','et-reunion',null,'standard'), ('tp-dinner','et-dinner',null,'intimate'),
  ('tp-newyear','et-newyear',null,'standard'), ('tp-conf','et-conf',null,'standard'), ('tp-launch','et-launch',null,'standard'),
  ('tp-expo','et-expo',null,'standard'), ('tp-offsite','et-offsite',null,'standard'), ('tp-awards','et-awards',null,'standard'),
  ('tp-opening','et-opening',null,'standard'), ('tp-college','et-college',null,'standard'), ('tp-sports','et-sports',null,'standard'),
  ('tp-concert','et-concert',null,'standard'), ('tp-charity','et-charity',null,'standard'), ('tp-community','et-community',null,'standard'),
  ('tp-other','et-other',null,'standard'), ('tp-bd-int','et-birthday',null,'intimate')
on conflict do nothing;

insert into event_template_items (template_id, category_id, sub_event, label, note, budget_share, sort) values
  ('tp-reception','k-venue','Reception','Venue or hall','',20,1), ('tp-reception','k-decor','Reception','Stage and hall decor','',15,2), ('tp-reception','k-cater','Reception','Catering','',35,3), ('tp-reception','k-photo','Reception','Photography','',10,4), ('tp-reception','k-anchor','Reception','Anchor or DJ','',5,5), ('tp-reception','k-light','Reception','Lighting','',5,6), ('tp-reception','k-sound','Reception','Sound system','',5,7), ('tp-reception','k-cake','Reception','Cake','',5,8),
  ('tp-anniv','k-venue','Main event','Venue or restaurant','',25,1), ('tp-anniv','k-decor','Main event','Decor','',15,2), ('tp-anniv','k-cater','Main event','Catering','',35,3), ('tp-anniv','k-cake','Main event','Cake','',10,4), ('tp-anniv','k-photo','Main event','Photography','',15,5),
  ('tp-babyshower','k-decor','Main event','Theme decor','',25,1), ('tp-babyshower','k-cater','Main event','Food and snacks','',35,2), ('tp-babyshower','k-cake','Main event','Cake','',10,3), ('tp-babyshower','k-photo','Main event','Photography','',15,4), ('tp-babyshower','k-gifts','Main event','Return gifts','',15,5),
  ('tp-naming','k-priest','Ceremony','Priest or officiant','',10,1), ('tp-naming','k-decor','Ceremony','Decor','',20,2), ('tp-naming','k-cater','Ceremony','Catering','',45,3), ('tp-naming','k-photo','Ceremony','Photography','',15,4), ('tp-naming','k-gifts','Ceremony','Return gifts','',10,5),
  ('tp-housewarm','k-priest','Ceremony','Priest for the blessing or puja','',10,1), ('tp-housewarm','k-decor','Ceremony','Flowers and entrance decor','',15,2), ('tp-housewarm','k-cater','Ceremony','Catering','',50,3), ('tp-housewarm','k-tent','Ceremony','Canopy for guests','',10,4), ('tp-housewarm','k-photo','Ceremony','Photography','',10,5), ('tp-housewarm','k-cool','Ceremony','Fans or coolers','',5,6),
  ('tp-retire','k-venue','Main event','Venue','',25,1), ('tp-retire','k-cater','Main event','Catering','',40,2), ('tp-retire','k-anchor','Main event','Host','',10,3), ('tp-retire','k-sound','Main event','Sound and mic','',5,4), ('tp-retire','k-photo','Main event','Photography','',10,5), ('tp-retire','k-gifts','Main event','Memento','',10,6),
  ('tp-memorial','k-venue','Service','Hall or venue','',25,1), ('tp-memorial','k-florist','Service','Flowers','',15,2), ('tp-memorial','k-tent','Service','Canopy and seating','',15,3), ('tp-memorial','k-cater','Service','Simple meal','',35,4), ('tp-memorial','k-sound','Service','Sound and mic','',10,5),
  ('tp-communion','k-decor','Church','Church decor','',15,1), ('tp-communion','k-photo','Church','Photography','',15,2), ('tp-communion','k-venue','Celebration','Hall','',20,3), ('tp-communion','k-cater','Celebration','Catering','',40,4), ('tp-communion','k-cake','Celebration','Cake','',10,5),
  ('tp-puja','k-priest','Puja','Priest','',20,1), ('tp-puja','k-florist','Puja','Flowers and garlands','',15,2), ('tp-puja','k-cater','Puja','Prasadam and meal','',40,3), ('tp-puja','k-tent','Puja','Canopy','',10,4), ('tp-puja','k-sound','Puja','Sound for chanting','',5,5), ('tp-puja','k-photo','Puja','Photography','',10,6),
  ('tp-iftar','k-venue','Gathering','Venue or hall','',20,1), ('tp-iftar','k-cater','Gathering','Iftar food','',55,2), ('tp-iftar','k-decor','Gathering','Lights and decor','',10,3), ('tp-iftar','k-furn','Gathering','Seating','',10,4), ('tp-iftar','k-sound','Gathering','Sound','',5,5),
  ('tp-festival','k-decor','Celebration','Festive decor','Pookalam, lamps or tree',20,1), ('tp-festival','k-cater','Celebration','Festive meal','Sadya, sweets or dinner',40,2), ('tp-festival','k-music','Celebration','Performers','',15,3), ('tp-festival','k-sound','Celebration','Sound','',5,4), ('tp-festival','k-light','Celebration','Lights','',10,5), ('tp-festival','k-photo','Celebration','Photography','',10,6),
  ('tp-temple','k-tent','Event','Pandal or canopy','',20,1), ('tp-temple','k-sound','Event','Sound system','',10,2), ('tp-temple','k-light','Event','Lighting','',10,3), ('tp-temple','k-power','Event','Generator','',10,4), ('tp-temple','k-cater','Event','Food service','',30,5), ('tp-temple','k-security','Event','Crowd staff','',10,6), ('tp-temple','k-clean','Event','Cleaning','',10,7),
  ('tp-kids','k-decor','Party','Theme decor and balloons','',25,1), ('tp-kids','k-kids','Party','Magician, games or mascot','',20,2), ('tp-kids','k-cake','Party','Cake','',15,3), ('tp-kids','k-cater','Party','Snacks','',25,4), ('tp-kids','k-gifts','Party','Return gifts','',10,5), ('tp-kids','k-photo','Party','Photography','',5,6),
  ('tp-reunion','k-venue','Main event','Venue','',30,1), ('tp-reunion','k-cater','Main event','Catering','',40,2), ('tp-reunion','k-sound','Main event','Sound and mic','',5,3), ('tp-reunion','k-anchor','Main event','Host or DJ','',10,4), ('tp-reunion','k-photo','Main event','Photography','',10,5), ('tp-reunion','k-print','Main event','Name tags and banners','',5,6),
  ('tp-dinner','k-venue','Dinner','Private room or home chef','',35,1), ('tp-dinner','k-cater','Dinner','Menu','',40,2), ('tp-dinner','k-decor','Dinner','Table styling','',15,3), ('tp-dinner','k-music','Dinner','Live musician','',10,4),
  ('tp-newyear','k-venue','Party','Venue','',25,1), ('tp-newyear','k-anchor','Party','DJ','',15,2), ('tp-newyear','k-sound','Party','Sound system','',10,3), ('tp-newyear','k-light','Party','Party lights','',10,4), ('tp-newyear','k-cater','Party','Food and drinks','',30,5), ('tp-newyear','k-security','Party','Security','',10,6),
  ('tp-conf','k-venue','Conference','Venue and rooms','',25,1), ('tp-conf','k-av','Conference','Projectors and LED screen','',10,2), ('tp-conf','k-sound','Conference','Mics and sound','',8,3), ('tp-conf','k-stage','Conference','Stage','',7,4), ('tp-conf','k-cater','Conference','Tea, lunch and snacks','',25,5), ('tp-conf','k-hosts','Conference','Registration desk and ushers','',5,6), ('tp-conf','k-brand','Conference','Banners and signage','',5,7), ('tp-conf','k-stream','Conference','Live streaming','',5,8), ('tp-conf','k-photo','Conference','Photography','',5,9), ('tp-conf','k-power','Conference','Generator backup','',5,10),
  ('tp-launch','k-venue','Launch','Venue','',20,1), ('tp-launch','k-stage','Launch','Stage and backdrop','',15,2), ('tp-launch','k-av','Launch','LED screen','',15,3), ('tp-launch','k-light','Launch','Show lighting','',10,4), ('tp-launch','k-anchor','Launch','Host','',5,5), ('tp-launch','k-brand','Launch','Branding','',10,6), ('tp-launch','k-cater','Launch','Catering','',15,7), ('tp-launch','k-video','Launch','Video coverage','',10,8),
  ('tp-expo','k-tent','Exhibition','Stalls or hangar','',25,1), ('tp-expo','k-furn','Exhibition','Furniture','',10,2), ('tp-expo','k-brand','Exhibition','Signage','',10,3), ('tp-expo','k-power','Exhibition','Power and generators','',10,4), ('tp-expo','k-light','Exhibition','Lighting','',10,5), ('tp-expo','k-security','Exhibition','Security','',10,6), ('tp-expo','k-clean','Exhibition','Cleaning','',5,7), ('tp-expo','k-cater','Exhibition','Food court','',15,8), ('tp-expo','k-hosts','Exhibition','Registration staff','',5,9),
  ('tp-offsite','k-venue','Outing','Resort or venue','',40,1), ('tp-offsite','k-cater','Outing','Meals','',30,2), ('tp-offsite','k-car','Outing','Transport','',15,3), ('tp-offsite','k-anchor','Outing','Games host','',10,4), ('tp-offsite','k-photo','Outing','Photography','',5,5),
  ('tp-awards','k-venue','Gala','Venue','',25,1), ('tp-awards','k-stage','Gala','Stage','',10,2), ('tp-awards','k-av','Gala','LED screen','',10,3), ('tp-awards','k-light','Gala','Show lighting','',10,4), ('tp-awards','k-anchor','Gala','Host','',5,5), ('tp-awards','k-gifts','Gala','Trophies','',10,6), ('tp-awards','k-cater','Gala','Dinner','',25,7), ('tp-awards','k-photo','Gala','Photography','',5,8),
  ('tp-opening','k-priest','Opening','Blessing or ribbon cutting','',10,1), ('tp-opening','k-decor','Opening','Entrance decor and balloons','',20,2), ('tp-opening','k-sound','Opening','Sound and mic','',10,3), ('tp-opening','k-brand','Opening','Banners','',15,4), ('tp-opening','k-cater','Opening','Snacks and sweets','',30,5), ('tp-opening','k-photo','Opening','Photography','',15,6),
  ('tp-college','k-stage','Event','Stage','',15,1), ('tp-college','k-sound','Event','Sound system','',15,2), ('tp-college','k-light','Event','Lighting','',10,3), ('tp-college','k-av','Event','LED screen','',10,4), ('tp-college','k-anchor','Event','Host or DJ','',10,5), ('tp-college','k-cater','Event','Food stalls','',20,6), ('tp-college','k-security','Event','Security','',10,7), ('tp-college','k-power','Event','Generator','',10,8),
  ('tp-sports','k-tent','Event','Canopies','',20,1), ('tp-sports','k-sound','Event','Public address','',10,2), ('tp-sports','k-furn','Event','Seating','',15,3), ('tp-sports','k-cater','Event','Refreshments','',20,4), ('tp-sports','k-gifts','Event','Trophies and medals','',15,5), ('tp-sports','k-security','Event','First aid and security','',10,6), ('tp-sports','k-photo','Event','Photography','',10,7),
  ('tp-concert','k-stage','Show','Stage and truss','',20,1), ('tp-concert','k-sound','Show','Concert sound','',20,2), ('tp-concert','k-light','Show','Show lighting','',15,3), ('tp-concert','k-av','Show','LED screens','',10,4), ('tp-concert','k-power','Show','Generators','',10,5), ('tp-concert','k-security','Show','Security and crowd control','',15,6), ('tp-concert','k-clean','Show','Cleaning','',5,7), ('tp-concert','k-stream','Show','Live streaming','',5,8),
  ('tp-charity','k-venue','Event','Venue','',25,1), ('tp-charity','k-cater','Event','Catering','',30,2), ('tp-charity','k-anchor','Event','Host','',10,3), ('tp-charity','k-sound','Event','Sound and mic','',10,4), ('tp-charity','k-brand','Event','Banners','',10,5), ('tp-charity','k-photo','Event','Photography','',15,6),
  ('tp-community','k-venue','Meeting','Hall','',30,1), ('tp-community','k-sound','Meeting','Mics and sound','',15,2), ('tp-community','k-furn','Meeting','Chairs and tables','',15,3), ('tp-community','k-cater','Meeting','Tea and snacks','',30,4), ('tp-community','k-av','Meeting','Projector','',10,5),
  ('tp-other','k-venue','Main event','Venue','Add or remove anything',30,1), ('tp-other','k-cater','Main event','Food and drinks','',35,2), ('tp-other','k-decor','Main event','Decor','',15,3), ('tp-other','k-sound','Main event','Sound','',10,4), ('tp-other','k-photo','Main event','Photography','',10,5),
  ('tp-bd-int','k-decor','Party','Home decor and balloons','',30,1), ('tp-bd-int','k-cake','Party','Cake','',20,2), ('tp-bd-int','k-cater','Party','Food for a small group','',40,3), ('tp-bd-int','k-photo','Party','One hour photo session','',10,4);
