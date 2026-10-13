(() => {
  'use strict';

  const SAVE_KEY = 'daemonarium.field-journal.v1';
  const CLASSIFICATIONS = ['Imp', 'Foliot', 'Djinn', 'Afrit', 'Marid'];
  const ELEMENTS = {
    Moss: { color: '#aec88f', pale: '#d4e3ae', dark: '#607b54', symbol: '✳' },
    Ember: { color: '#e1936e', pale: '#f5bd8e', dark: '#92573f', symbol: '♨' },
    Tide: { color: '#8dbec1', pale: '#c2e1d7', dark: '#4c7e83', symbol: '≈' },
    Gale: { color: '#b5a5d1', pale: '#ddd0ee', dark: '#74678f', symbol: '⌁' },
    Stone: { color: '#cfb57f', pale: '#e9d49d', dark: '#84704d', symbol: '◇' },
    Gloam: { color: '#9dabbf', pale: '#ced5e2', dark: '#5b687f', symbol: '☾' },
  };
  const SPECIES = [
    { name: 'Brindle', element: 'Moss', nature: 'a patient little wanderer', region: 'Moonfen', hp: 40, atk: 9, def: 10, spd: 8, moves: ['Briar Flick', 'Soft Guard', 'Spore Drift', 'Rootwake'] },
    { name: 'Cinderling', element: 'Ember', nature: 'bright-eyed and difficult to startle', region: 'Moonfen', hp: 34, atk: 12, def: 7, spd: 11, moves: ['Kindle', 'Ashen Pounce', 'Ember Veil', 'Wildfire'] },
    { name: 'Morrowisp', element: 'Gloam', nature: 'curious about every new name', region: 'Moonfen', hp: 32, atk: 11, def: 8, spd: 13, moves: ['Dusklight', 'Hush', 'Nightglass', 'Veilbreak'] },
    { name: 'Pollenwing', element: 'Gale', nature: 'cheerful in the company of rain', region: 'Glasswood', hp: 35, atk: 10, def: 8, spd: 13, moves: ['Petal Gust', 'Crosswind', 'Quietus', 'Skyward'] },
    { name: 'Rill', element: 'Tide', nature: 'quiet, watchful, and quietly proud', region: 'Glasswood', hp: 43, atk: 9, def: 11, spd: 7, moves: ['Rill Rush', 'Tidepool', 'Foamguard', 'Highwater'] },
    { name: 'Vellum', element: 'Stone', nature: 'an old soul in a newly found shape', region: 'Glasswood', hp: 39, atk: 11, def: 12, spd: 6, moves: ['Flint Song', 'Foldspace', 'Slate Shell', 'Faultline'] },
    { name: 'Ashveil', element: 'Ember', nature: 'warm-hearted, with a streak of mischief', region: 'Cinder Shrine', hp: 38, atk: 14, def: 8, spd: 10, moves: ['Kindle', 'Sear', 'Ember Veil', 'Wildfire'] },
    { name: 'Mica', element: 'Gale', nature: 'drawn to old stories and open windows', region: 'Cinder Shrine', hp: 36, atk: 11, def: 9, spd: 14, moves: ['Petal Gust', 'Crosswind', 'Quietus', 'Skyward'] },
    { name: 'Nacre', element: 'Tide', nature: 'gentle until the tide turns', region: 'Hush Archive', hp: 47, atk: 12, def: 13, spd: 8, moves: ['Rill Rush', 'Tidepool', 'Foamguard', 'Highwater'] },
    { name: 'Lacuna', element: 'Gloam', nature: 'a little wary of being called a daemon', region: 'Hush Archive', hp: 40, atk: 15, def: 9, spd: 13, moves: ['Dusklight', 'Hush', 'Nightglass', 'Veilbreak'] },
  ];
  const MOVE_DATA = {
    'Briar Flick': [10, 'Moss'], 'Soft Guard': [0, 'Moss'], 'Spore Drift': [12, 'Moss'], Rootwake: [17, 'Moss'],
    Kindle: [11, 'Ember'], 'Ashen Pounce': [14, 'Ember'], 'Ember Veil': [0, 'Ember'], Wildfire: [20, 'Ember'], Sear: [19, 'Ember'],
    Dusklight: [11, 'Gloam'], Hush: [0, 'Gloam'], Nightglass: [15, 'Gloam'], Veilbreak: [20, 'Gloam'],
    'Petal Gust': [10, 'Gale'], Crosswind: [14, 'Gale'], Quietus: [0, 'Gale'], Skyward: [19, 'Gale'],
    'Rill Rush': [12, 'Tide'], Tidepool: [0, 'Tide'], Foamguard: [14, 'Tide'], Highwater: [20, 'Tide'],
    'Flint Song': [11, 'Stone'], Foldspace: [0, 'Stone'], 'Slate Shell': [14, 'Stone'], Faultline: [19, 'Stone'],
  };
  const REGIONS = [
    { name: 'Moonfen', subtitle: 'The low country remembers every footstep.', level: [2, 5], sky: '#89917a', back: '#a9a783', ground: '#526951', far: '#607b63', encounter: ['Brindle', 'Cinderling', 'Morrowisp'], unlock: 0 },
    { name: 'Glasswood', subtitle: 'The leaves hold the light a little too long.', level: [4, 8], sky: '#879d8c', back: '#b6bf9c', ground: '#4e765f', far: '#63836a', encounter: ['Pollenwing', 'Rill', 'Vellum'], unlock: 1 },
    { name: 'Cinder Shrine', subtitle: 'Someone still tends the lamps beneath the hill.', level: [7, 12], sky: '#b0785f', back: '#d2a576', ground: '#785a4b', far: '#846248', encounter: ['Ashveil', 'Mica', 'Vellum'], unlock: 4 },
    { name: 'Hush Archive', subtitle: 'The drowned shelves keep what the living misplace.', level: [10, 16], sky: '#657f8b', back: '#a3bec0', ground: '#3c6368', far: '#4f7778', encounter: ['Nacre', 'Lacuna', 'Morrowisp'], unlock: 7 },
  ];
  const ITEMS = {
    iron: { name: 'Iron Sigil', description: 'A simple mark for a new agreement.', kind: 'binding', price: 28, bonus: 0 },
    silver: { name: 'Silver Thread', description: 'A patient, finer-spun binding.', kind: 'binding', price: 72, bonus: 0.17 },
    heart: { name: 'Heart-Knot', description: 'A rare knot that holds through resistance.', kind: 'binding', price: 150, bonus: 0.32 },
    tonic: { name: 'Moonwater Tonic', description: 'Restore 32 health to one spirit.', kind: 'heal', price: 24 },
    balm: { name: 'Contract Balm', description: 'Restore 22 fixed points of stability.', kind: 'contract', price: 90 },
  };
  const NAV = [
    ['field', '⌂', 'The Field'], ['codex', '❋', 'Daemonarium'], ['coven', '◉', 'The Coven'], ['satchel', '▤', 'Satchel'], ['hall', '⌁', 'Broken Contracts'],
  ];

  const uid = () => Math.random().toString(36).slice(2, 9);
  const clone = (value) => JSON.parse(JSON.stringify(value));
  const speciesByName = (name) => SPECIES.find((s) => s.name === name) || SPECIES[0];
  const stageForLevel = (level) => level >= 23 ? 4 : level >= 16 ? 3 : level >= 10 ? 2 : level >= 5 ? 1 : 0;
  const classificationFor = (spirit) => CLASSIFICATIONS[stageForLevel(spirit.level)];
  const elementStyle = (element) => ELEMENTS[element] || ELEMENTS.Moss;
  const maxHp = (spirit) => spirit.baseHp + (spirit.level - 1) * 4 + stageForLevel(spirit.level) * 4;
  const xpNeed = (level) => level * 24;
  const cap = (n, low, high) => Math.max(low, Math.min(high, n));

  function sprite(element, size = 96, seed = 'a') {
    const e = elementStyle(element);
    const unique = `${element.toLowerCase()}-${seed.replace(/[^a-z0-9]/gi, '')}`;
    let body;
    if (element === 'Moss') body = `<path d="M28 63c-5-12 0-27 13-34l-2-17 14 10 12-14 2 20c11 8 15 23 8 35-6 12-37 15-47 0Z" fill="url(#coat-${unique})"/><path d="M38 28 36 16l12 9M63 25l9-12 2 16" fill="${e.dark}" stroke="${e.dark}" stroke-linejoin="round"/><path d="M42 52c4-10 19-12 25-2l-2 15c-8 6-19 4-24-3Z" fill="${e.pale}"/><path d="M49 53h2m11 0h2" stroke="#26322c" stroke-width="3" stroke-linecap="round"/><path d="M50 61q5 5 10 0" fill="none" stroke="#66734f" stroke-width="2"/><path d="M37 31q-8-12 2-18 1 12 11 14m22 1q10-10 5-18-3 11-13 13" fill="${e.color}"/>`;
    else if (element === 'Ember') body = `<path d="M30 58c-3-15 4-29 18-34 2-10 11-14 11-14 2 10 0 15 8 21 11 9 12 24 4 33-11 12-36 9-41-6Z" fill="url(#coat-${unique})"/><path d="M42 48c3-8 17-10 23-2l-1 17c-7 6-17 4-22-3Z" fill="${e.pale}"/><path d="M48 51h2m11 0h2" stroke="#3a302a" stroke-width="3" stroke-linecap="round"/><path d="M51 60q5 4 10-1" fill="none" stroke="#92573f" stroke-width="2"/><path d="M32 61Q15 57 21 40q8 9 14 9" fill="${e.color}"/><path d="M55 77q-8 9-19 3m25-1q6 7 14 2" fill="none" stroke="${e.dark}" stroke-width="5" stroke-linecap="round"/>`;
    else if (element === 'Tide') body = `<path d="M22 54q2-25 28-28 25-1 29 25-2 22-25 26-25 1-32-23Z" fill="url(#coat-${unique})"/><path d="m29 39-10-11 19 4m29 3 13-12-5 20" fill="${e.color}"/><path d="M43 50c6-8 19-6 23 2l-4 14q-11 5-20-2Z" fill="${e.pale}"/><path d="M47 51h2m12 0h2" stroke="#28383c" stroke-width="3" stroke-linecap="round"/><path d="M52 61q6 3 10-1" fill="none" stroke="#5b8281" stroke-width="2"/><path d="M25 57q-13 4-11 16 12-2 18-11" fill="${e.dark}"/><path d="M56 27q0-11 9-15 3 12-3 19" fill="${e.pale}"/>`;
    else if (element === 'Gale') body = `<path d="M48 46C13 9 14 62 39 59c-14 24 20 25 16 2 19 17 39-6 15-16 19-18-7-36-22 1Z" fill="${e.dark}" opacity=".8"/><path d="M50 33q-17-19-20-8 1 10 19 20m9-9q19-18 21-7-1 10-19 21m-22 2q-13 20-3 22 9-2 13-20m12 0q16 17 22 9 1-10-17-16" fill="${e.color}" stroke="${e.pale}" stroke-width="2"/><ellipse cx="54" cy="52" rx="13" ry="20" fill="url(#coat-${unique})"/><path d="M44 48q-7-12-6-19m19 19q8-12 8-19" fill="none" stroke="${e.pale}" stroke-width="3" stroke-linecap="round"/><path d="M48 49h1m9 0h1" stroke="#303044" stroke-width="3" stroke-linecap="round"/><path d="M49 59q4 3 8 0" fill="none" stroke="#635c78" stroke-width="2"/>`;
    else if (element === 'Stone') body = `<path d="m28 37 11-19 15 6 14-7 12 21-5 29-22 11-25-12Z" fill="url(#coat-${unique})" stroke="${e.pale}" stroke-opacity=".45" stroke-width="2"/><path d="m34 38-12-8 2 19 9 3m35-15 12-9-2 20-10 4" fill="${e.dark}"/><path d="M39 49q9-13 21-3l5 18q-15 10-28-2Z" fill="${e.pale}"/><path d="M44 50h2m13 0h2" stroke="#37342d" stroke-width="3" stroke-linecap="round"/><path d="M48 62q6 3 11-1" fill="none" stroke="#857452" stroke-width="2"/><path d="m48 25 7-12 9 14m-28 47-7 8m42-7 8 8" fill="none" stroke="${e.pale}" stroke-width="4" stroke-linecap="round"/>`;
    else body = `<path d="M25 57q-3-27 27-33 27 4 28 31-1 23-27 25-25-1-28-23Z" fill="url(#coat-${unique})"/><path d="m33 37-2-22 17 12m17 1 15-14-3 23" fill="${e.dark}"/><path d="M39 48q8-11 21-5l8 16q-13 12-29 0Z" fill="${e.pale}"/><path d="M44 50h2m14 0h2" stroke="#30303b" stroke-width="3" stroke-linecap="round"/><path d="M48 62q6 3 12-1" fill="none" stroke="#657287" stroke-width="2"/><path d="M76 63q15 2 12-12-10 4-13 10" fill="${e.color}"/><path d="M55 24v-8m-6 8h12" stroke="${e.pale}" stroke-width="2" stroke-linecap="round"/>`;
    return `<svg viewBox="0 0 100 100" width="${size}" height="${size}" role="img" aria-label="${element} spirit" xmlns="http://www.w3.org/2000/svg"><defs><linearGradient id="coat-${unique}" x1=".2" y1="0" x2=".85" y2="1"><stop stop-color="${e.pale}"/><stop offset="1" stop-color="${e.color}"/></linearGradient></defs><ellipse cx="53" cy="86" rx="25" ry="5" fill="#0c1411" opacity=".35"/><g stroke="#26352e" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round">${body}</g><path d="M27 44q-5-8-12-6 3 8 11 11m53-9q8-6 14-2-4 8-13 9" fill="none" stroke="${e.pale}" stroke-width="2" opacity=".75"/><circle cx="20" cy="25" r="2" fill="${e.pale}" opacity=".8"/><circle cx="82" cy="19" r="1.5" fill="${e.pale}" opacity=".75"/><path d="M77 31l2 3 3 1-3 2-2 3-1-3-3-2 3-1Z" fill="${e.pale}" opacity=".8"/></svg>`;
  }

  function makeSpirit(speciesName, level, wild = false) {
    const spec = speciesByName(speciesName);
    const id = uid();
    const epithets = ['of the Reedlight', 'the Far-Listener', 'under Glass', 'of Quiet Water', 'the Candle-Sleeper', 'of Two Names'];
    const spirit = {
      id, species: spec.name, name: wild ? `${spec.name} ${weightedPick(epithets)}` : spec.name, element: spec.element, nature: spec.nature,
      level, xp: 0, baseHp: spec.hp, hp: 0, atk: spec.atk + (level - 1) * 1.2,
      def: spec.def + (level - 1) * 0.8, spd: spec.spd + (level - 1) * 0.7,
      contract: wild ? 100 : 82, soulbound: false, moves: [spec.moves[0], spec.moves[1]],
      seen: false, caughtAt: '', history: ['An individual met beyond the veil.'], inTeam: false,
    };
    spirit.hp = maxHp(spirit);
    return spirit;
  }

  function initialState() {
    const starter = makeSpirit('Brindle', 3);
    starter.name = 'Brindle'; starter.contract = 100; starter.inTeam = true; starter.soulbound = true;
    starter.seen = true; starter.caughtAt = 'Moonfen'; starter.history = ['Your first meeting, beneath the fen-lights.'];
    return {
      view: 'home', region: 'Moonfen', day: 1, noteCount: 2, money: 120, discoveries: 1, battlesWon: 0, surveyed: 0,
      spirits: [starter], soulboundId: starter.id, activeId: starter.id,
      inventory: { iron: 5, silver: 1, heart: 0, tonic: 3, balm: 1 },
      seenSpecies: ['Brindle'], regionsUnlocked: ['Moonfen'], escaped: [], lost: [], journal: [
        { text: 'Your field journal begins in the low country.', time: 'FIELD NOTE 001', icon: '⌂' },
        { text: 'Brindle chose to walk beside you.', time: 'FIRST CONTRACT', icon: '✳' },
      ], battle: null, modal: null, filters: { element: 'All' }, toast: '',
    };
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(SAVE_KEY);
      if (!raw) return initialState();
      const parsed = JSON.parse(raw);
      if (!parsed || !Array.isArray(parsed.spirits) || !parsed.spirits.length) return initialState();
      const fresh = initialState();
      const state = { ...fresh, ...parsed };
      state.view = 'home';
      state.modal = null; state.toast = '';
      if (!state.spirits.some((s) => s.id === state.soulboundId && s.inTeam)) {
        const member = state.spirits.find((s) => s.inTeam) || state.spirits[0];
        member.inTeam = true; member.soulbound = true; state.soulboundId = member.id;
      }
      return state;
    } catch { return initialState(); }
  }

  let state = loadState();
  const app = document.getElementById('app');
  let toastTimer;
  const esc = (text = '') => String(text).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const isSoul = (spirit) => spirit.id === state.soulboundId;
  const team = () => state.spirits.filter((s) => s.inTeam);
  const lead = () => state.spirits.find((s) => s.id === state.activeId) || team()[0];
  const getRegion = () => REGIONS.find((r) => r.name === state.region) || REGIONS[0];
  const inventoryCount = (id) => Number(state.inventory[id] || 0);
  const shortTime = () => `FIELD NOTE ${String(state.noteCount || state.journal.length).padStart(3, '0')}`;

  function save() {
    try { localStorage.setItem(SAVE_KEY, JSON.stringify(state)); } catch { /* The game remains playable when storage is blocked. */ }
  }
  function note(text, icon = '✦') {
    state.noteCount = (state.noteCount || state.journal.length) + 1;
    state.journal.unshift({ text, time: shortTime(), icon });
    state.journal = state.journal.slice(0, 7);
  }
  function showToast(message) {
    const node = document.querySelector('.toast');
    if (!node) { state.toast = message; return; }
    node.textContent = message; node.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => document.querySelector('.toast')?.classList.remove('show'), 2100);
  }
  function finishUpdate(message = '') {
    save(); render();
    if (message) showToast(message);
  }

  function regionArt(region) {
    return `<svg class="map-art" viewBox="0 0 1000 430" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><defs><linearGradient id="horizon" x2="0" y2="1"><stop stop-color="${region.sky}"/><stop offset="1" stop-color="${region.back}"/></linearGradient><linearGradient id="land" x2="0" y2="1"><stop stop-color="${region.far}"/><stop offset="1" stop-color="${region.ground}"/></linearGradient><radialGradient id="sun"><stop stop-color="#fff0c3" stop-opacity=".9"/><stop offset="1" stop-color="#f5dca2" stop-opacity="0"/></radialGradient></defs><rect width="1000" height="430" fill="url(#horizon)"/><circle cx="733" cy="100" r="126" fill="url(#sun)"/><circle cx="733" cy="100" r="48" fill="#eadbb1" opacity=".68"/><path d="M0 212 Q120 162 254 208T498 193T745 205T1000 178V430H0Z" fill="${region.far}" opacity=".76"/><path d="M0 270 Q136 212 258 269T505 245T763 276T1000 235V430H0Z" fill="url(#land)"/><path d="M0 332 Q148 290 281 338T522 309T782 343T1000 301V430H0Z" fill="${region.ground}"/><path d="M235 430Q390 382 461 330t169-12q-73 49-69 112H235Z" fill="#c1b891" opacity=".22"/><g fill="#24372e" opacity=".66"><path d="M128 282q-17-72 4-110l-18-45 37 29 30-38-5 57q25 55 4 111Z"/><path d="M180 293q-13-47 2-78l-13-35 28 22 20-27-3 38q19 40 3 81Z"/><path d="M856 272q-14-61 4-99l-15-41 31 26 24-33-4 47q23 44 5 101Z"/><path d="M915 286q-11-45 4-72l-12-33 25 20 18-25-3 36q18 35 4 74Z"/></g><g fill="#d4d39a" opacity=".72"><circle cx="304" cy="270" r="2"/><circle cx="325" cy="296" r="1.7"/><circle cx="347" cy="260" r="1.5"/><circle cx="378" cy="285" r="2"/><circle cx="705" cy="300" r="2"/><circle cx="734" cy="277" r="1.5"/><circle cx="770" cy="306" r="2"/></g><path d="M534 308q18-21 37-1m-21 13q20-24 42-3m-11 19q20-19 39-2" fill="none" stroke="#d5ce9a" stroke-width="3" stroke-linecap="round" opacity=".7"/><path d="M543 321q-4-18 3-31m48 38q-2-21 6-32m-37 23q-2-17 5-27" stroke="#d6d28f" stroke-width="3" stroke-linecap="round" opacity=".8"/></svg>`;
  }

  function progressBar(value, max, kind = '') {
    const percent = cap((value / max) * 100, 0, 100);
    const low = kind === 'hp' && percent < 28 ? ' hp-low' : '';
    return `<div class="bar ${kind === 'contract' ? 'contract' : ''}${low}"><i style="width:${percent}%"></i></div>`;
  }

  function navButton([id, icon, label], mobile = false) {
    const active = state.view === id ? ' active' : '';
    const badge = id === 'hall' && state.escaped.length ? `<span class="nav-meta">${state.escaped.length}</span>` : '';
    return `<button class="nav-item${active}" data-action="navigate" data-view="${id}" aria-label="${label}" ${mobile ? '' : `title="${label}"`}><span class="nav-icon">${icon}</span><span class="nav-copy">${label}</span>${badge}</button>`;
  }

  function sideSpirit(spirit) {
    return `<div class="party-card${spirit.id === state.activeId ? ' active-spirit' : ''}" data-action="set-active" data-id="${spirit.id}" tabindex="0" role="button" aria-label="Make ${esc(spirit.name)} your active spirit"><div class="portrait">${sprite(spirit.element, 41, spirit.id)}</div><div class="party-info"><div class="party-name">${esc(spirit.name)} ${isSoul(spirit) ? '<span class="soul-gem">✦</span>' : ''}</div><div class="party-sub">${classificationFor(spirit)} · Lv. ${spirit.level}</div><div class="party-hp">${progressBar(spirit.hp, maxHp(spirit), 'hp')}<span class="hp-number">${spirit.hp}/${maxHp(spirit)}</span></div></div></div>`;
  }

  function sidebars() {
    const party = team();
    const stable = party.length ? Math.round(party.reduce((sum, s) => sum + s.contract, 0) / party.length) : 0;
    const mainNav = NAV.map((item) => navButton(item)).join('');
    return `<aside class="sidebar"><div class="brand"><div class="brand-mark">D</div><div class="brand-copy"><div class="brand-name">Daemonarium</div><div class="brand-sub">A field journal</div></div></div><div class="nav-label">FIELDWORK</div><nav class="nav-list" aria-label="Main navigation">${mainNav}</nav><div class="sidebar-bottom"><div class="weather-note"><div class="weather-line"><span class="weather-place">${esc(state.region)}</span><span class="weather-icon">☼</span></div><div class="weather-detail">A stillness over the grass</div></div><div class="save-line"><span class="save-dot"></span> Journal saved locally</div></div></aside><main class="main"><div class="mobile-top"><div class="brand"><div class="brand-mark">D</div><div class="brand-copy"><div class="brand-name">Daemonarium</div><div class="brand-sub">A field journal</div></div></div><div class="resource"><span class="coin">◈</span>${state.money} shards</div></div><header class="topbar"><div class="breadcrumb"><span>FIELD JOURNAL</span><span>/</span><span class="current">${esc(NAV.find(([id]) => id === state.view)?.[2] || (state.view === 'home' ? 'Home' : 'The Field'))}</span></div><div class="top-actions"><div class="resource"><span class="coin">◈</span>${state.money} shards</div><div class="avatar" title="Field magician">M</div></div></header><section class="view" id="view-content">${renderView()}</section></main><aside class="rightbar"><div class="journal-head"><h2>Your coven</h2><span>${party.length} / 6</span></div><div class="party-list">${party.length ? party.map(sideSpirit).join('') : '<div class="quiet-note">No spirits in your party.</div>'}</div><div class="party-caption"><span>ACTIVE TEAM</span><button class="text-link" data-action="navigate" data-view="coven">MANAGE</button></div><div class="side-divider"></div><div class="contract-summary"><div class="contract-summary-head"><span>CONTRACT TENSION</span><span>${party.every(isSoul) ? 'ANCHORED' : `${stable}%`}</span></div>${progressBar(stable, 100, 'contract')}<p>Only battle wears a bond. Travel leaves it whole.</p></div><div class="section-head"><h2>Recent notes</h2><span class="eyebrow">${String(state.journal.length).padStart(2, '0')}</span></div><div class="journal-list">${state.journal.slice(0, 4).map((entry) => `<div class="journal-entry"><span class="entry-dot">${entry.icon}</span><div>${esc(entry.text)}<time>${esc(entry.time)}</time></div></div>`).join('')}</div><div class="footer-mark">✦ &nbsp; Listen before you bind</div></aside><nav class="mobile-nav" aria-label="Main navigation">${NAV.map((item) => navButton(item, true)).join('')}</nav><div class="toast" role="status" aria-live="polite"></div>${renderModal()}</div>`;
  }

  function regionButtons() {
    return REGIONS.map((region, i) => {
      const unlocked = state.regionsUnlocked.includes(region.name);
      const current = state.region === region.name;
      return `<button class="region-chip${current ? ' selected' : ''}${unlocked ? '' : ' locked'}" data-action="select-region" data-region="${esc(region.name)}" ${unlocked ? '' : 'disabled'}>${unlocked ? '' : '⌑ '}${String(i + 1).padStart(2, '0')} &nbsp;${esc(region.name.toUpperCase())}</button>`;
    }).join('');
  }

  function fieldView() {
    const region = getRegion();
    const known = new Set(state.seenSpecies).size;
    const localSpecies = region.encounter.map((name) => SPECIES.find((s) => s.name === name)).filter(Boolean);
    const discoveredInRegion = localSpecies.filter((s) => state.seenSpecies.includes(s.name));
    return `<div class="page-heading"><div><div class="eyebrow">FIELD JOURNAL &nbsp;·&nbsp; DAY ${String(state.day).padStart(2, '0')}</div><h1>Between the veil</h1><p>The spirit world keeps its own counsel. Walk gently.</p></div><div class="heading-side"><strong>${known} / ${SPECIES.length}</strong><br>SPIRITS RECORDED</div></div><div class="hero-map">${regionArt(region)}<div class="map-shade"></div><div class="map-copy"><div class="eyebrow">REGION 0${REGIONS.indexOf(region) + 1} &nbsp;·&nbsp; ${region.level[0]}–${region.level[1]} WANDERING</div><h2>${esc(region.name)}</h2><p>${esc(region.subtitle)}</p></div><div class="map-index">ATLAS &nbsp; ${REGIONS.indexOf(region) + 1} / 04</div><div class="map-stamp">SPIRIT<br>COUNTRY<br>✳</div><div class="map-controls">${regionButtons()}</div></div><div class="section-head"><h2>What calls from here</h2><span class="eyebrow">${discoveredInRegion.length} KNOWN OF ${localSpecies.length}</span></div><div class="dispatch-grid"><article class="dispatch-card"><div class="dispatch-illustration">${sprite(localSpecies[0]?.element || 'Moss', 62, `grass-${region.name}`)}</div><div class="dispatch-copy"><div class="eyebrow">ENCOUNTER GROUNDS</div><h3>Spirit Grass</h3><p>Choose to step inside when you are ready.</p><button class="mini-button" data-action="enter-grass">Walk the grass &nbsp;↗</button></div></article><article class="dispatch-card"><div class="dispatch-illustration"><svg viewBox="0 0 64 64" width="53" height="53" aria-hidden="true"><path d="M17 43h30M22 42l3-19 9-7 9 7 3 19" fill="none" stroke="#b8c99a" stroke-width="2"/><path d="m25 24 9 6 9-6m-18 9 18 0M32 17V9m-5 4h10" fill="none" stroke="#7e9e82" stroke-width="2"/><circle cx="32" cy="32" r="24" fill="none" stroke="#809879" stroke-dasharray="2 4"/></svg></div><div class="dispatch-copy"><div class="eyebrow">SLOW LOOKING</div><h3>Read the signs</h3><p>A quiet survey may turn up something useful.</p><button class="mini-button" data-action="survey">Survey this place &nbsp;↗</button></div></article></div><div class="section-head"><h2>Field notes</h2><button class="text-link" data-action="navigate" data-view="codex">OPEN DAEMONARIUM &nbsp;↗</button></div><div class="panel"><div class="table-list">${state.journal.slice(0, 3).map((entry) => `<div class="table-row"><div><div class="row-title">${esc(entry.text)}</div><div class="row-sub">${esc(entry.time)}</div></div><span class="entry-dot">${entry.icon}</span></div>`).join('')}</div></div>`;
  }

  function spiritCard(spirit, compact = false) {
    const teamLabel = spirit.inTeam ? (spirit.id === state.activeId ? 'ACTIVE' : 'IN YOUR COVEN') : 'AT THE SANCTUM';
    const stage = stageForLevel(spirit.level);
    const xpPercent = (spirit.xp / xpNeed(spirit.level)) * 100;
    return `<article class="spirit-card"><div class="spirit-card-top"><div class="spirit-art">${sprite(spirit.element, 66, spirit.id)}</div><div><h3 class="spirit-title">${esc(spirit.name)}${isSoul(spirit) ? ' <span class="soul-gem">✦</span>' : ''}</h3><div class="spirit-id">${classificationFor(spirit)} &nbsp;·&nbsp; LEVEL ${spirit.level}</div><div class="spirit-badges"><span class="badge type-badge">${elementStyle(spirit.element).symbol} ${esc(spirit.element)}</span><span class="badge">${stage > 0 ? `FORM ${stage + 1}` : 'AWAKENED'}</span></div></div></div><div class="spirit-bars"><div class="meter-line"><span>HEALTH</span>${progressBar(spirit.hp, maxHp(spirit), 'hp')}<strong>${spirit.hp}</strong></div><div class="meter-line"><span>BOND</span>${isSoul(spirit) ? `<span class="quiet-note" style="grid-column:span 2;color:#e5c67d">SOUL-BOUND · DOES NOT FADE</span>` : `${progressBar(spirit.contract, 100, 'contract')}<strong>${spirit.contract}</strong>`}</div><div class="meter-line"><span>GROWTH</span>${progressBar(spirit.xp, xpNeed(spirit.level))}<strong>${Math.floor(xpPercent)}%</strong></div></div><div class="spirit-foot"><span>${teamLabel} · ${esc(spirit.caughtAt || 'RECLAIMED')}</span><button class="spirit-action" data-action="spirit-detail" data-id="${spirit.id}">OPEN RECORD ↗</button></div></article>`;
  }

  function codexView() {
    const known = state.spirits.slice().sort((a, b) => a.name.localeCompare(b.name));
    const missing = SPECIES.filter((spec) => !state.seenSpecies.includes(spec.name));
    const escapedCards = state.escaped.map((spirit) => `<article class="spirit-card"><div class="spirit-card-top"><div class="spirit-art">${sprite(spirit.element, 66, spirit.id)}</div><div><h3 class="spirit-title">${esc(spirit.name)}</h3><div class="spirit-id">${classificationFor(spirit)} · LAST SEEN ${esc(spirit.caughtAt || 'BEYOND THE VEIL')}</div><div class="spirit-badges"><span class="badge" style="color:#dfa398;border-color:#694740">BROKEN CONTRACT</span><span class="badge">${spirit.attempts} REBINDINGS LEFT</span></div></div></div><div class="spirit-foot"><span>THE INDIVIDUAL REMAINS</span><button class="spirit-action" data-action="navigate" data-view="hall">SEEK THEM ↗</button></div></article>`).join('');
    return `<div class="page-heading"><div><div class="eyebrow">OBSERVATION &nbsp;·&nbsp; KNOWLEDGE IS NEVER COMPLETE</div><h1>The Daemonarium</h1><p>A record of individuals met, and a little of what they allow to be known.</p></div><div class="heading-side"><strong>${state.seenSpecies.length} / ${SPECIES.length}</strong><br>CLASSIFIED</div></div><div class="stat-grid"><div class="stat-card"><div class="eyebrow">INDIVIDUALS</div><div class="stat-value">${state.spirits.length}</div><div class="stat-foot">bound and remembered</div></div><div class="stat-card"><div class="eyebrow">SPECIES</div><div class="stat-value">${state.seenSpecies.length}<span style="color:var(--quiet);font-size:15px"> / ${SPECIES.length}</span></div><div class="stat-foot">entered in the record</div></div><div class="stat-card"><div class="eyebrow">AGREEMENTS</div><div class="stat-value">${state.discoveries}</div><div class="stat-foot">encounters that mattered</div></div><div class="stat-card"><div class="eyebrow">EVOLUTIONS</div><div class="stat-value">${state.spirits.reduce((sum, s) => sum + stageForLevel(s.level), 0)}</div><div class="stat-foot">new forms carried forward</div></div></div><div class="section-head"><h2>Those who walk with you</h2><span class="eyebrow">${known.length} INDIVIDUAL${known.length === 1 ? '' : 'S'}</span></div>${known.length ? `<div class="spirit-grid">${known.map((s) => spiritCard(s)).join('')}</div>` : '<div class="empty-state"><div class="big-symbol">✳</div><h3>No names yet.</h3><p>Enter the Spirit Grass and meet whoever is listening.</p><button class="primary-button" data-action="navigate" data-view="field">RETURN TO THE FIELD</button></div>'}<div class="section-head"><h2>Not yet encountered</h2><span class="eyebrow">THE UNKNOWN</span></div><div class="panel"><div class="table-list">${missing.length ? missing.map((spec) => `<div class="table-row"><div><div class="row-title" style="color:#849087">Unrecorded spirit</div><div class="row-sub">${esc(spec.region)} · ${esc(spec.element)} affinity</div></div><span class="quiet-note">? ? ?</span></div>`).join('') : '<div class="quiet-note">Every known presence has found its way into the journal.</div>'}</div></div>${escapedCards ? `<div class="section-head"><h2>Beyond your reach</h2><span class="eyebrow">THE HALL AWAITS</span></div><div class="spirit-grid">${escapedCards}</div>` : ''}`;
  }

  function covenView() {
    const party = team();
    const stored = state.spirits.filter((s) => !s.inTeam);
    const soul = state.spirits.find((s) => isSoul(s));
    return `<div class="page-heading"><div><div class="eyebrow">PARTY &nbsp;·&nbsp; UP TO SIX INDIVIDUALS</div><h1>The Coven</h1><p>Your companions are people with names. Every contract has a history.</p></div><div class="heading-side"><strong>✦ ${esc(soul?.name || 'NONE')}</strong><br>SOUL-BOUND</div></div><div class="panel contract-card"><div><div class="eyebrow">A BOND BY CHOICE</div><h2 class="panel-title">The Soul Bound</h2><p class="panel-sub">One companion, protected from contract deterioration. This safeguard carries no battle advantage.</p></div><div class="contract-big-number">✦</div></div><div class="section-head"><h2>Your active coven</h2><span class="eyebrow">${party.length} / 06</span></div>${party.length ? `<div class="spirit-grid">${party.map((s) => spiritCard(s)).join('')}</div>` : '<div class="empty-state"><h3>The coven is quiet.</h3></div>'}<div class="section-head"><h2>Keep in your party</h2><span class="eyebrow">THE SANCTUM</span></div>${stored.length ? `<div class="panel"><div class="table-list">${stored.map((s) => `<div class="table-row"><div style="display:flex;align-items:center;gap:11px"><div class="portrait">${sprite(s.element, 38, s.id)}</div><div><div class="row-title">${esc(s.name)} · Lv. ${s.level}</div><div class="row-sub">${classificationFor(s)} · stored contracts do not fade</div></div></div><div class="item-buttons"><button class="mini-button" data-action="add-party" data-id="${s.id}" ${party.length >= 6 ? 'disabled' : ''}>ADD TO COVEN</button></div></div>`).join('')}</div></div>` : '<div class="panel"><p class="panel-sub">There are no stored spirits. Bind someone new out in the field to grow your coven.</p></div>'}<div class="section-head"><h2>Designate your Soul Bound</h2><span class="eyebrow">CHANGE AT ANY TIME</span></div><div class="panel"><div class="table-list">${party.map((s) => `<div class="table-row"><div><div class="row-title">${esc(s.name)}${isSoul(s) ? ' ✦' : ''}</div><div class="row-sub">${isSoul(s) ? 'Their contract cannot deteriorate.' : 'A new designation immediately removes protection from your current Soul Bound.'}</div></div><button class="mini-button" data-action="set-soul" data-id="${s.id}" ${isSoul(s) ? 'disabled' : ''}>${isSoul(s) ? 'SOUL-BOUND' : 'DESIGNATE'}</button></div>`).join('')}</div></div>`;
  }

  function satchelView() {
    const inv = Object.entries(ITEMS);
    return `<div class="page-heading"><div><div class="eyebrow">SUPPLIES &nbsp;·&nbsp; ${state.money} SHARDS</div><h1>The Satchel</h1><p>Binding supplies, ordinary medicine, and a little room for repair.</p></div><div class="heading-side"><strong>◈ ${state.money}</strong><br>FIELD SHARDS</div></div><div class="section-head"><h2>On hand</h2><span class="eyebrow">THE THINGS YOU CARRY</span></div><div class="panel"><div class="table-list">${inv.map(([id, item]) => `<div class="table-row"><div style="display:flex;align-items:center;gap:11px"><span class="entry-dot" style="color:${item.kind === 'binding' ? 'var(--green)' : item.kind === 'heal' ? 'var(--sky)' : 'var(--gold)'}">${item.kind === 'binding' ? '⌘' : item.kind === 'heal' ? '✚' : '✦'}</span><div><div class="row-title">${esc(item.name)}</div><div class="row-sub">${esc(item.description)}</div></div></div><div class="item-buttons"><span class="item-amount">× ${inventoryCount(id)}</span>${item.kind !== 'binding' ? `<button class="mini-button" data-action="use-item" data-item="${id}" ${inventoryCount(id) <= 0 ? 'disabled' : ''}>USE</button>` : ''}</div></div>`).join('')}</div></div><div class="section-head"><h2>At the apothecary</h2><span class="eyebrow">SUPPLIES ARE NEVER FREE</span></div><div class="panel"><div class="table-list">${inv.map(([id, item]) => `<div class="table-row"><div><div class="row-title">${esc(item.name)}</div><div class="row-sub">${esc(item.description)}</div></div><div class="item-buttons"><span class="shop-price">◈ ${item.price}</span><button class="mini-button" data-action="buy-item" data-item="${id}" ${state.money < item.price ? 'disabled' : ''}>BUY</button></div></div>`).join('')}</div></div><div class="section-head"><h2>Make good on a bond</h2><span class="eyebrow">A PRIVATE RITUAL</span></div><div class="panel"><div class="table-list">${state.spirits.filter((s) => !isSoul(s) && s.inTeam && s.contract < 100).map((s) => `<div class="table-row"><div><div class="row-title">${esc(s.name)} · ${s.contract}% stability</div><div class="row-sub">A balm restores 22 fixed stability points.</div></div><button class="mini-button" data-action="restore" data-id="${s.id}" ${inventoryCount('balm') < 1 ? 'disabled' : ''}>USE BALM · ${inventoryCount('balm')}</button></div>`).join('') || '<div class="quiet-note">Every present contract is intact, or already beyond repair.</div>'}</div><p class="panel-sub" style="margin-top:12px">Health and Contract Stability are separate. A tonic cannot repair a bond; a balm cannot mend a body.</p></div><div class="section-head"><h2>Journal</h2><span class="eyebrow">THIS BROWSER ONLY</span></div><div class="panel"><p class="panel-sub">Your field journal saves automatically in this browser. Container restarts will not erase it.</p><button class="danger-button" style="margin-top:14px" data-action="reset-save">Begin a new journal</button></div>`;
  }

  function hallView() {
    if (!state.escaped.length) return `<div class="page-heading"><div><div class="eyebrow">THE HALL OF BROKEN CONTRACTS</div><h1>What slipped away</h1><p>The spirits remember the agreements that failed.</p></div></div><div class="empty-state"><div class="big-symbol">⌁</div><h3>The Hall is quiet.</h3><p>No contracts have broken. Ordinary travel and time never erode a bond; battle does. Your Soul Bound is always protected.</p><button class="secondary-button" data-action="navigate" data-view="field">RETURN TO THE FIELD</button></div><div class="section-head"><h2>On reclamation</h2><span class="eyebrow">A WAY BACK, NOT A PROMISE</span></div><div class="panel"><p class="panel-sub">If an ordinary contract fails, that same spirit can be sought here. Win a reclamation battle and offer a binding item. You have three attempts to make a new agreement; their identity and growth remain unchanged.</p></div>`;
    return `<div class="page-heading"><div><div class="eyebrow">THE HALL OF BROKEN CONTRACTS</div><h1>What slipped away</h1><p>They are the same individuals you knew. They may not welcome you back.</p></div><div class="heading-side"><strong>${state.escaped.length}</strong><br>AWAITING RECLAMATION</div></div><div class="panel" style="margin-bottom:18px"><p class="panel-sub">Each spirit waits here with their own history, level, and abilities intact. Defeat them to attempt a new contract. Three binding attempts are allowed; after that, the individual is lost for good.</p></div><div class="spirit-grid">${state.escaped.map((s) => `<article class="spirit-card"><div class="spirit-card-top"><div class="spirit-art">${sprite(s.element, 66, s.id)}</div><div><h3 class="spirit-title">${esc(s.name)}</h3><div class="spirit-id">${classificationFor(s)} · LEVEL ${s.level}</div><div class="spirit-badges"><span class="badge" style="color:#dfa398;border-color:#694740">${s.attempts} ATTEMPTS LEFT</span></div></div></div><div class="spirit-foot"><span>LAST KNOWN: ${esc(s.caughtAt || 'THE FIELD')}</span><button class="spirit-action" data-action="reclaim" data-id="${s.id}" ${!team().some((x) => x.hp > 0) ? 'disabled' : ''}>CHALLENGE ↗</button></div></article>`).join('')}</div><div class="section-head"><h2>Those who are gone</h2><span class="eyebrow">PERMANENTLY LOST</span></div>${state.lost.length ? `<div class="panel"><div class="table-list">${state.lost.map((s) => `<div class="table-row"><div><div class="row-title">${esc(s.name)}</div><div class="row-sub">A contract spent; an individual beyond reach.</div></div><span class="quiet-note">LOST</span></div>`).join('')}</div></div>` : '<div class="panel"><p class="panel-sub">No spirit has been lost beyond reclamation.</p></div>'}`;
  }

  function battleHud(spirit, player = false) {
    const hp = spirit.hp ?? maxHp(spirit);
    return `<div class="battle-hud${player ? ' player-hud' : ''}"><div class="battle-hud-line"><span class="battle-name">${esc(spirit.name)}</span><span class="battle-level">LV. ${spirit.level}</span></div>${progressBar(hp, maxHp(spirit), 'hp')}<div class="battle-hp-copy">${hp} / ${maxHp(spirit)} HEALTH</div></div>`;
  }

  function battleView() {
    const battle = state.battle;
    if (!battle) return fieldView();
    const enemy = battle.enemy;
    const player = state.spirits.find((s) => s.id === battle.activeId) || lead();
    const region = getRegion();
    const result = battle.outcome;
    const actionButtons = result ? `<div class="result-panel"><h2>${result === 'win' ? 'The spirit is listening.' : result === 'loss' ? 'The field falls still.' : 'The spirit slips away.'}</h2><p>${result === 'win' ? (battle.type === 'reclaim' ? 'You have one chance to offer the original contract again.' : 'A defeated spirit can still choose whether to be bound.') : result === 'loss' ? 'A defeat is hard on ordinary contracts. Your Soul Bound will remain beside you.' : 'No bond was made. The grass grows over the trace.'}</p>${result === 'win' ? (battle.type === 'wild' ? `<div class="result-reward"><span>✦ ${battle.xpAward || 0} GROWTH</span><span>◈ ${battle.coinAward || 0} SHARDS</span></div><div class="item-buttons" style="justify-content:center"><button class="primary-button" data-action="open-binding">OFFER A BINDING</button><button class="secondary-button" data-action="release-wild">LET THEM GO</button></div>` : `<div class="result-reward"><span>RECLAMATION</span><span>✦ ${Math.max(0, battle.target?.attempts ?? 0)} ATTEMPTS REMAIN</span></div><div class="item-buttons" style="justify-content:center"><button class="primary-button" data-action="open-binding">OFFER A NEW CONTRACT</button><button class="secondary-button" data-action="leave-reclaim">LEAVE THE HALL</button></div>`) : `<button class="secondary-button" data-action="close-battle">RETURN TO THE FIELD</button>`}</div>` : `<div class="battle-actions"><div class="move-grid">${player.moves.map((move) => { const data = MOVE_DATA[move] || [10, player.element]; return `<button class="move-button" data-action="use-move" data-move="${esc(move)}"><div class="move-name">${esc(move)}</div><div class="move-detail"><span class="move-type">${data[1]} · ${data[0] || 'GUARD'}</span><span>∞</span></div></button>`; }).join('')}</div><div class="battle-utility"><button class="secondary-button" data-action="open-switch">Switch</button><button class="secondary-button" data-action="open-heal">Use tonic</button><button class="secondary-button" data-action="flee" ${battle.type === 'reclaim' ? 'disabled' : ''}>Flee</button></div></div>`;
    return `<div class="page-heading"><div><div class="eyebrow">${battle.type === 'reclaim' ? 'RECLAMATION TRIAL' : 'A MEETING IN THE GRASS'} &nbsp;·&nbsp; ${esc(region.name).toUpperCase()}</div><h1>${battle.type === 'reclaim' ? 'A difficult return' : 'Make room for a spirit'}</h1><p>${result ? 'The encounter has ended.' : 'Take your time. The old rules of a battle still apply.'}</p></div><div class="heading-side"><strong>TURN ${battle.turn}</strong><br>${battle.type === 'reclaim' ? 'IN THE HALL' : 'WILD ENCOUNTER'}</div></div><div class="battle-wrap">${regionArt(region)}<div class="battle-region-label">${battle.type === 'reclaim' ? 'HALL OF BROKEN CONTRACTS' : esc(region.name.toUpperCase())}</div><div class="battle-platform enemy-platform"></div><div class="battle-sprite">${sprite(enemy.element, 138, enemy.id)}</div>${battleHud(enemy)}<div class="battle-platform player-platform"></div><div class="player-battle-sprite">${sprite(player.element, 112, player.id)}</div>${battleHud(player, true)}</div><div class="battle-log" aria-live="polite">${esc(battle.log)}</div>${actionButtons}`;
  }

  function homeView() {
    return `<div class="landing-page"><section class="landing-hero"><img class="landing-art" src="images/daemonarium-banner.png" alt="A glimpse into the spirit world"><div class="landing-shade"></div><div class="landing-copy"><div class="eyebrow">A CREATURE-COLLECTION RPG ABOUT TRUST</div><h1>Beyond the veil, <em>every spirit has a name.</em></h1><p>Magicians call them daemons. They call themselves spirits. Step into a mysterious world where every contract is a choice between power, trust, and freedom.</p><div class="landing-actions"><button class="primary-button" data-action="navigate" data-view="field">ENTER THE FIELD <span aria-hidden="true">→</span></button><button class="secondary-button" data-action="navigate" data-view="codex">BROWSE THE DAEMONARIUM</button></div></div><div class="landing-stamp" aria-hidden="true">LISTEN<br>BEFORE<br>YOU BIND</div></section><div class="landing-intro"><div class="eyebrow">THE WORLD OF DAEMONARIUM</div><h2>Power is easy to measure.<br><em>A bond is harder to know.</em></h2><p>Explore uncanny regions, meet intelligent spirits, and build a coven through turn-based battles and magical agreements. Each spirit carries its own personality, history, and future.</p></div><div class="landing-cards"><article class="landing-card"><span class="landing-number">01 / WANDER</span><h3>Follow the signs</h3><p>Cross the Spirit Grass when you are ready to meet what waits within. Every region has its own creatures, discoveries, and secrets.</p></article><article class="landing-card"><span class="landing-number">02 / MAKE A CHOICE</span><h3>Earn a contract</h3><p>Use elemental moves and careful tactics to overcome a spirit, then offer a binding sigil—or let them return to the wild.</p></article><article class="landing-card"><span class="landing-number">03 / KEEP THE BOND</span><h3>Grow together</h3><p>Your companions learn, evolve, and keep the memories that make them themselves. Battles can strain an ordinary contract; one Soul Bound stays safe. A broken bond can be reclaimed if the spirit returns.</p></article></div><section class="landing-question"><span class="landing-quote-mark" aria-hidden="true">“</span><div><div class="eyebrow">A QUESTION WITHOUT AN EASY ANSWER</div><h2>Does a contract create a partnership?</h2><p>Or does it ask who gets to name, protect, and choose the future of a spirit?</p></div><button class="text-link" data-action="navigate" data-view="field">MAKE YOUR FIRST JOURNEY <span aria-hidden="true">→</span></button></section></div>`;
  }

  function renderView() {
    if (state.battle && state.view === 'field') return battleView();
    if (state.view === 'home') return homeView();
    if (state.view === 'codex') return codexView();
    if (state.view === 'coven') return covenView().replace(/<button class="spirit-action" data-action="spirit-detail" data-id="([^"]+)">.*?<\/button>/g, (button, id) => `${button}${isSoul(state.spirits.find((s) => s.id === id)) ? '' : `<button class="spirit-action" data-action="store-spirit" data-id="${id}">STORE AT SANCTUM</button>`}`);
    if (state.view === 'satchel') return satchelView();
    if (state.view === 'hall') return hallView();
    return fieldView();
  }

  function renderModal() {
    const modal = state.modal;
    if (!modal) return '';
    let body = '';
    if (modal.kind === 'binding') {
      const enemy = state.battle?.enemy;
      body = `<div class="modal-creature">${enemy ? sprite(enemy.element, 115, enemy.id) : ''}</div><div class="table-list">${['iron', 'silver', 'heart'].map((id) => { const item = ITEMS[id]; const count = inventoryCount(id); const chance = enemy ? bindingChance(enemy, id) : 0; return `<div class="table-row"><div><div class="row-title">${esc(item.name)}</div><div class="row-sub">${esc(item.description)}</div></div><div class="item-buttons"><span class="item-amount">~${Math.round(chance * 100)}% &nbsp;×${count}</span><button class="mini-button" data-action="bind" data-item="${id}" ${count <= 0 ? 'disabled' : ''}>OFFER</button></div></div>`; }).join('')}</div><p>Each attempt uses one binding item. Stronger individuals are harder to bind; their weakened state helps.</p>`;
    } else if (modal.kind === 'switch') {
      const candidates = team().filter((s) => s.hp > 0 && s.id !== (state.battle?.activeId || state.activeId));
      body = candidates.length ? `<div class="table-list">${candidates.map((s) => `<div class="table-row"><div style="display:flex;gap:10px;align-items:center"><div class="portrait">${sprite(s.element, 38, s.id)}</div><div><div class="row-title">${esc(s.name)} · Lv. ${s.level}</div><div class="row-sub">${s.hp}/${maxHp(s)} health</div></div></div><button class="mini-button" data-action="switch-to" data-id="${s.id}">SEND OUT</button></div>`).join('')}</div>` : '<p>No other conscious spirit can take the field.</p>';
    } else if (modal.kind === 'heal') {
      const candidates = team().filter((s) => s.hp < maxHp(s) && (!state.battle || s.id === state.battle.activeId));
      body = candidates.length && inventoryCount('tonic') ? `<div class="table-list">${candidates.map((s) => `<div class="table-row"><div><div class="row-title">${esc(s.name)} · ${s.hp}/${maxHp(s)}</div><div class="row-sub">Restore up to 32 health.</div></div><button class="mini-button" data-action="heal-spirit" data-id="${s.id}">USE TONIC</button></div>`).join('')}</div>` : `<p>${inventoryCount('tonic') ? 'Everyone is already at full health.' : 'Your satchel is out of tonics.'}</p>`;
    } else if (modal.kind === 'use-item') {
      const candidates = team().filter((s) => s.hp < maxHp(s) && (!state.battle || s.id === state.battle.activeId));
      body = inventoryCount('tonic') && candidates.length ? `<div class="table-list">${candidates.map((s) => `<div class="table-row"><div><div class="row-title">${esc(s.name)} · ${s.hp}/${maxHp(s)}</div><div class="row-sub">Restore up to 32 health.</div></div><button class="mini-button" data-action="heal-spirit" data-id="${s.id}">USE TONIC</button></div>`).join('')}</div>` : '<p>You have no tonic to use, or every spirit is already whole.</p>';
    } else if (modal.kind === 'detail') {
      const spirit = state.spirits.find((s) => s.id === modal.id);
      body = spirit ? `<div class="modal-creature">${sprite(spirit.element, 115, spirit.id)}</div><div class="stat-grid" style="grid-template-columns:repeat(3,1fr)"><div class="stat-card"><div class="eyebrow">POWER</div><div class="stat-value">${Math.round(spirit.atk)}</div></div><div class="stat-card"><div class="eyebrow">GUARD</div><div class="stat-value">${Math.round(spirit.def)}</div></div><div class="stat-card"><div class="eyebrow">PACE</div><div class="stat-value">${Math.round(spirit.spd)}</div></div></div><p>${esc(spirit.name)} is ${esc(spirit.nature)}. Met in ${esc(spirit.caughtAt || 'the spirit world')}. ${spirit.history.map(esc).join(' ')}</p><div class="section-head"><h2>Remembered moves</h2></div><div class="spirit-badges">${spirit.moves.map((m) => `<span class="badge">${esc(m)}</span>`).join('')}</div>` : '';
    } else if (modal.kind === 'learn-move') {
      body = `<p>${esc(modal.spiritName)} has learned <strong>${esc(modal.move)}</strong>. Choose one move to leave behind, or keep the four already carried.</p><div class="table-list">${modal.currentMoves.map((move) => `<div class="table-row"><div><div class="row-title">${esc(move)}</div><div class="row-sub">${MOVE_DATA[move]?.[0] || 'Support'} · ${esc(MOVE_DATA[move]?.[1] || 'Technique')}</div></div><button class="mini-button" data-action="replace-move" data-old="${esc(move)}">FORGET & LEARN</button></div>`).join('')}</div><div class="modal-actions"><button class="secondary-button" data-action="decline-move">KEEP EXISTING MOVES</button></div>`;
    } else if (modal.kind === 'confirm-reset') {
      body = '<p>This removes the field journal saved in this browser and begins a fresh expedition.</p><div class="modal-actions"><button class="secondary-button" data-action="close-modal">KEEP JOURNAL</button><button class="danger-button" data-action="confirm-reset">ERASE & BEGIN AGAIN</button></div>';
    }
    return `<div class="modal-scrim" data-action="scrim-close"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><div class="modal-head"><div><div class="eyebrow">${modal.kind === 'binding' ? 'A CHOICE OF CONTRACT' : modal.kind === 'detail' ? 'INDIVIDUAL RECORD' : modal.kind === 'confirm-reset' ? 'START OVER' : 'FIELD DECISION'}</div><h2 id="modal-title">${esc(modal.title || 'A moment of care')}</h2></div><button class="modal-close" data-action="close-modal" aria-label="Close dialog">×</button></div>${body}</section></div>`;
  }

  function render() {
    app.innerHTML = sidebars().replaceAll('class="brand"', 'class="brand brand-home" role="button" tabindex="0" data-action="navigate" data-view="home" aria-label="Daemonarium home"').replace('<aside class="sidebar">', '<div class="layout"><aside class="sidebar">');
    if (state.toast) { const message = state.toast; state.toast = ''; showToast(message); }
  }

  function weightedPick(list) {
    return list[Math.floor(Math.random() * list.length)];
  }

  function enterGrass() {
    const region = getRegion();
    const spec = speciesByName(weightedPick(region.encounter));
    const level = Math.floor(Math.random() * (region.level[1] - region.level[0] + 1)) + region.level[0];
    const enemy = makeSpirit(spec.name, level, true);
    enemy.hp = maxHp(enemy);
    state.battle = { type: 'wild', enemy, activeId: lead()?.id, participants: lead() ? [lead().id] : [], turn: 1, outcome: null, log: `${enemy.name} turns from the grass. It seems to be ${enemy.nature}.` };
    state.view = 'field'; save(); render();
  }

  function battleEnd(outcome, line) {
    const battle = state.battle;
    if (!battle) return;
    battle.outcome = outcome;
    battle.log = line;
    if (outcome === 'win') {
      battle.xpAward = Math.round(11 + battle.enemy.level * 4 + (battle.enemy.hp === 0 ? 4 : 0));
      battle.coinAward = Math.round(8 + battle.enemy.level * 2);
      state.money += battle.coinAward;
      state.battlesWon += 1;
      for (const id of battle.participants) {
        const spirit = state.spirits.find((s) => s.id === id);
        if (spirit) awardXp(spirit, battle.xpAward);
      }
      weakenContracts(battle.participants, false);
      if (battle.type === 'wild') {
        state.discoveries += 1;
        if (!state.seenSpecies.includes(battle.enemy.species)) {
          state.seenSpecies.push(battle.enemy.species);
          note(`${battle.enemy.species} entered the Daemonarium.`, '❋');
        }
        unlockRegions();
      }
      note(`${battle.enemy.name} was defeated. The coven learned from the meeting.`, '✦');
      return;
    }
    if (outcome === 'loss') {
      for (const id of battle.participants) {
        const spirit = state.spirits.find((s) => s.id === id);
        if (spirit && spirit.hp > 0) spirit.hp = Math.max(1, spirit.hp - 4);
      }
      weakenContracts(battle.participants, true);
      note(`The encounter turned. Ordinary contracts suffered in the retreat.`, '⌁');
      state.money = Math.max(0, state.money - 5);
    }
    if (outcome === 'flee') {
      weakenContracts(battle.participants, false);
      note(`You left the encounter before it could deepen.`, '⌂');
    }
  }

  function weakenContracts(participants, lostBattle) {
    const escaped = [];
    for (const id of new Set(participants)) {
      const spirit = state.spirits.find((s) => s.id === id);
      if (!spirit || isSoul(spirit)) continue;
      spirit.contract = Math.max(0, spirit.contract - (lostBattle ? 18 : 5));
      if (spirit.hp <= 0) spirit.contract = Math.max(0, spirit.contract - 12);
      if (spirit.contract <= 0) escaped.push(spirit);
    }
    for (const spirit of escaped) {
      state.spirits = state.spirits.filter((s) => s.id !== spirit.id);
      spirit.inTeam = false; spirit.soulbound = false; spirit.attempts = 3; spirit.hp = Math.max(1, Math.ceil(maxHp(spirit) * 0.6));
      state.escaped.push(spirit);
      if (state.soulboundId === spirit.id) {
        const anchor = team()[0];
        if (anchor) { state.soulboundId = anchor.id; anchor.soulbound = true; }
      }
      if (state.activeId === spirit.id) state.activeId = state.soulboundId;
      note(`${spirit.name}'s contract broke. They are waiting in the Hall.`, '⌁');
    }
  }

  function awardXp(spirit, amount) {
    spirit.xp += amount;
    let changed = false;
    while (spirit.xp >= xpNeed(spirit.level) && spirit.level < 30) {
      spirit.xp -= xpNeed(spirit.level);
      spirit.level += 1;
      spirit.atk += 1.2; spirit.def += 0.8; spirit.spd += 0.7;
      spirit.hp = Math.min(maxHp(spirit), spirit.hp + 5);
      const priorStage = stageForLevel(spirit.level - 1);
      const nextStage = stageForLevel(spirit.level);
      if (nextStage > priorStage) {
        spirit.history.push(`Evolved into a ${CLASSIFICATIONS[nextStage]} at level ${spirit.level}, carrying the old self forward.`);
        note(`${spirit.name} evolved: ${CLASSIFICATIONS[priorStage]} → ${CLASSIFICATIONS[nextStage]}.`, '✦');
        changed = true;
      }
      const spec = speciesByName(spirit.species);
      const learned = spec.moves[Math.min(3, 2 + Math.floor((spirit.level - 4) / 4))];
      if (spirit.level >= 4 && spirit.level % 4 === 0 && learned && !spirit.moves.includes(learned)) {
        if (spirit.moves.length < 4) spirit.moves.push(learned);
        else if (!state.modal) state.modal = { kind: 'learn-move', title: 'A new technique', spiritId: spirit.id, spiritName: spirit.name, move: learned, currentMoves: [...spirit.moves] };
      }
      changed = true;
    }
    if (changed) state.toast = `${spirit.name} reached level ${spirit.level}.`;
  }

  function unlockRegions() {
    for (const region of REGIONS) {
      if (state.discoveries >= region.unlock && !state.regionsUnlocked.includes(region.name)) {
        state.regionsUnlocked.push(region.name);
        note(`A new path opens toward ${region.name}.`, '⌂');
        state.toast = `New path discovered: ${region.name}`;
      }
    }
  }

  function bindingChance(target, itemId) {
    const item = ITEMS[itemId];
    const weak = 1 - target.hp / maxHp(target);
    const tier = stageForLevel(target.level);
    return cap(0.42 + weak * 0.36 + item.bonus - tier * 0.055 - Math.max(0, target.level - 4) * 0.009, 0.13, 0.93);
  }

  function offerBinding(itemId) {
    const battle = state.battle;
    const target = battle?.type === 'reclaim' ? battle.target : battle?.enemy;
    if (!battle || battle.outcome !== 'win' || inventoryCount(itemId) <= 0 || !target) return;
    state.inventory[itemId] -= 1;
    const chance = bindingChance(target, itemId);
    if (Math.random() < chance) {
      if (battle.type === 'reclaim') {
        target.contract = 62;
        target.hp = Math.max(1, target.hp);
        target.attempts = 3;
        target.history.push('The broken contract was mended in the Hall.');
        target.inTeam = team().length < 6;
        state.spirits.push(target);
        state.escaped = state.escaped.filter((s) => s.id !== target.id);
        state.soulboundId = state.soulboundId || target.id;
        if (!team().some((s) => isSoul(s))) { state.soulboundId = target.id; target.soulbound = true; target.inTeam = true; }
        if (target.inTeam) state.activeId = target.id;
        note(`${target.name} returned after a new agreement in the Hall.`, '✦');
        state.battle = null; state.modal = null; state.view = 'hall'; finishUpdate(`${target.name} chose to return.`); return;
      }
      target.contract = 72;
      target.hp = Math.max(1, target.hp);
      target.seen = true; target.caughtAt = state.region;
      target.history = [`Your first agreement was made in ${state.region}.`];
      target.inTeam = team().length < 6;
      state.spirits.push(target);
      if (!state.seenSpecies.includes(target.species)) state.seenSpecies.push(target.species);
      note(`${target.name} made a contract with you in ${state.region}.`, '✦');
      state.battle = null; state.modal = null;
      finishUpdate(`${target.name} chose to walk beside you.`); return;
    }
    if (battle.type === 'reclaim') {
      target.attempts -= 1;
      battle.target.attempts = target.attempts;
      if (target.attempts <= 0) {
        state.escaped = state.escaped.filter((s) => s.id !== target.id);
        state.lost.push(target);
        note(`${target.name} refused every return. Their trail went quiet.`, '⌁');
        state.battle = null;
        finishUpdate(`${target.name} is lost for good.`); return;
      }
      battle.log = `${target.name} refused the ${ITEMS[itemId].name}. The old grievance remains. ${target.attempts} attempts remain.`;
      state.modal = { kind: 'binding', title: 'Try another thread' };
      finishUpdate(`${target.name} refused. ${target.attempts} attempts remain.`); return;
    }
    battle.log = `${target.name} felt the ${ITEMS[itemId].name} settle, then slipped free. You can try again.`;
    state.modal = { kind: 'binding', title: 'The spirit hesitates' };
    finishUpdate('The contract was refused. You can offer another sigil.');
  }

  function damageFor(attacker, defender, move) {
    const [power, element] = MOVE_DATA[move] || [10, attacker.element];
    if (power === 0) {
      attacker.def += 2;
      return { damage: 0, text: `${attacker.name} gathered itself with ${move}. Its guard rose.` };
    }
    const chart = { Moss: { Tide: 1.25, Ember: 0.76 }, Ember: { Moss: 1.25, Gale: 0.8 }, Tide: { Ember: 1.25, Stone: 0.82 }, Gale: { Moss: 1.18, Tide: 0.82 }, Stone: { Ember: 1.2, Gale: 0.82 }, Gloam: { Gale: 1.2, Moss: 0.82 } };
    const advantage = chart[element]?.[defender.element] || 1;
    const damage = Math.max(4, Math.round((power + attacker.atk * 0.65 - defender.def * 0.32 + Math.random() * 5) * advantage));
    return { damage, text: `${attacker.name} used ${move}${advantage > 1.1 ? ' — the affinity rang true' : ''}!` };
  }

  function chooseEnemyMove(enemy) {
    return enemy.moves[Math.floor(Math.random() * enemy.moves.length)] || `${enemy.element} Strike`;
  }

  function combatTurn(move) {
    const battle = state.battle;
    if (!battle || battle.outcome) return;
    const player = state.spirits.find((s) => s.id === battle.activeId);
    if (!player || player.hp <= 0) return;
    if (!battle.participants.includes(player.id)) battle.participants.push(player.id);
    const isPlayerFirst = player.spd >= battle.enemy.spd || Math.random() < 0.55;
    const turnLines = [];
    const playerAction = () => {
      const result = damageFor(player, battle.enemy, move);
      battle.enemy.hp = Math.max(0, battle.enemy.hp - result.damage);
      turnLines.push(result.text);
    };
    const enemyAction = () => {
      if (battle.enemy.hp <= 0) return;
      const enemyMove = chooseEnemyMove(battle.enemy);
      const result = damageFor(battle.enemy, player, enemyMove);
      player.hp = Math.max(0, player.hp - result.damage);
      turnLines.push(`${result.text}${player.hp === 0 ? ` ${player.name} has fainted.` : ''}`);
    };
    if (isPlayerFirst) { playerAction(); if (battle.enemy.hp > 0) enemyAction(); }
    else { enemyAction(); if (player.hp > 0) playerAction(); }
    if (turnLines.length) battle.log = turnLines.join(' ');
    if (!battle.outcome) {
      if (battle.enemy.hp <= 0) battleEnd('win', `${battle.log} ${battle.enemy.name} lowered its guard.`);
      else if (team().every((s) => s.hp <= 0)) battleEnd('loss', `${battle.log} The coven can no longer hold the field.`);
      else { battle.turn += 1; state.activeId = player.id; }
    }
    save(); render();
  }

  function applySwitch(id) {
    const battle = state.battle;
    const next = state.spirits.find((s) => s.id === id && s.inTeam && s.hp > 0);
    if (!battle || !next || next.id === battle.activeId) return;
    const old = state.spirits.find((s) => s.id === battle.activeId);
    if (old && !battle.participants.includes(old.id)) battle.participants.push(old.id);
    if (!battle.participants.includes(next.id)) battle.participants.push(next.id);
    battle.activeId = next.id; state.activeId = next.id;
    battle.log = `${old?.name || 'Your companion'} withdrew. ${next.name} entered the field.`;
    const enemyMove = chooseEnemyMove(battle.enemy);
    const response = damageFor(battle.enemy, next, enemyMove);
    next.hp = Math.max(0, next.hp - response.damage);
    battle.log += ` ${response.text}${next.hp === 0 ? ` ${next.name} has fainted.` : ''}`;
    battle.turn += 1;
    if (team().every((s) => s.hp <= 0)) battleEnd('loss', `${battle.log} The coven can no longer hold the field.`);
    state.modal = null; save(); render();
  }

  function useTonic(id, inBattle = false) {
    const spirit = state.spirits.find((s) => s.id === id);
    if (inBattle && state.battle && id !== state.battle.activeId) return;
    if (!spirit || inventoryCount('tonic') <= 0 || spirit.hp >= maxHp(spirit)) return;
    state.inventory.tonic -= 1;
    const restored = Math.min(32, maxHp(spirit) - spirit.hp);
    spirit.hp += restored;
    if (inBattle && state.battle && !state.battle.outcome) {
      const enemyMove = chooseEnemyMove(state.battle.enemy);
      const result = damageFor(state.battle.enemy, spirit, enemyMove);
      spirit.hp = Math.max(0, spirit.hp - result.damage);
      state.battle.log = `A Moonwater Tonic restored ${restored} health. ${state.battle.enemy.name} answered with ${enemyMove}.`;
      state.battle.turn += 1;
      if (team().every((s) => s.hp <= 0)) battleEnd('loss', `${state.battle.log} The coven can no longer hold the field.`);
    }
    state.modal = null;
    finishUpdate(`${spirit.name} restored ${restored} health.`);
  }

  function setReclaim(id) {
    const target = state.escaped.find((s) => s.id === id);
    const fighter = team().find((s) => s.hp > 0);
    if (!target || !fighter) return;
    const copyTarget = target;
    copyTarget.hp = Math.max(1, Math.min(copyTarget.hp, maxHp(copyTarget)));
    state.battle = { type: 'reclaim', target: copyTarget, enemy: copyTarget, activeId: fighter.id, participants: [fighter.id], turn: 1, outcome: null, log: `${target.name} waits in the Hall, carrying the whole of their old life.` };
    state.view = 'hall'; save(); render();
  }

  function addParty(id) {
    const spirit = state.spirits.find((s) => s.id === id);
    if (!spirit || team().length >= 6) return;
    spirit.inTeam = true;
    if (spirit.hp <= 0) spirit.hp = 1;
    note(`${spirit.name} joined the active coven.`, '◉');
    finishUpdate(`${spirit.name} joined your party.`);
  }

  function buyItem(id) {
    const item = ITEMS[id];
    if (!item || state.money < item.price) return;
    state.money -= item.price; state.inventory[id] = inventoryCount(id) + 1;
    finishUpdate(`${item.name} added to your satchel.`);
  }

  function survey() {
    state.day += 1; state.surveyed += 1;
    const find = Math.random();
    if (find < 0.52) {
      const earned = Math.round(7 + Math.random() * 13);
      state.money += earned;
      note(`You found ${earned} field shards among the old stones.`, '◈');
      finishUpdate(`The survey uncovered ${earned} shards.`);
    } else if (find < 0.83) {
      const id = Math.random() < 0.75 ? 'iron' : 'tonic';
      state.inventory[id] = inventoryCount(id) + 1;
      note(`A ${ITEMS[id].name} was tucked beneath the roots.`, '✦');
      finishUpdate(`Found one ${ITEMS[id].name}.`);
    } else {
      const spec = speciesByName(weightedPick(getRegion().encounter));
      state.seenSpecies = [...new Set([...state.seenSpecies, spec.name])];
      state.discoveries += 1; unlockRegions();
      note(`You noticed a ${spec.name} watching from the grass.`, '❋');
      finishUpdate(`${spec.name} added to the Daemonarium's field notes.`);
    }
  }

  function releaseWild() {
    const battle = state.battle;
    if (!battle || battle.type !== 'wild' || battle.outcome !== 'win') return;
    note(`${battle.enemy.name} was allowed to return to the grass.`, '⌂');
    state.battle = null; finishUpdate('The spirit returned to the wild.');
  }

  function handleAction(action, target) {
    const id = target.dataset.id;
    switch (action) {
      case 'navigate': if (state.battle && !['home', 'field'].includes(target.dataset.view)) break; state.modal = null; state.view = target.dataset.view; finishUpdate(); break;
      case 'select-region': state.region = target.dataset.region; finishUpdate(); break;
      case 'enter-grass': enterGrass(); break;
      case 'survey': survey(); break;
      case 'set-active': {
        const spirit = state.spirits.find((s) => s.id === id && s.inTeam && s.hp > 0);
        if (spirit && !state.battle) { state.activeId = id; finishUpdate(`${spirit.name} is ready to lead.`); }
        break;
      }
      case 'spirit-detail': state.modal = { kind: 'detail', title: state.spirits.find((s) => s.id === id)?.name || 'Spirit record', id }; save(); render(); break;
      case 'set-soul': {
        const spirit = state.spirits.find((s) => s.id === id && s.inTeam);
        if (spirit) { const old = state.spirits.find((s) => s.id === state.soulboundId); if (old) old.soulbound = false; state.soulboundId = spirit.id; spirit.soulbound = true; note(`${spirit.name} became your Soul Bound.`, '✦'); finishUpdate(`${spirit.name} is your Soul Bound.`); }
        break;
      }
      case 'add-party': addParty(id); break;
      case 'store-spirit': {
        const spirit = state.spirits.find((s) => s.id === id && s.inTeam);
        if (spirit && !isSoul(spirit) && team().length > 1) {
          spirit.inTeam = false;
          if (state.activeId === spirit.id) state.activeId = state.soulboundId;
          note(`${spirit.name} was given a quiet place at the sanctum.`, '◉');
          finishUpdate(`${spirit.name} is safely stored.`);
        }
        break;
      }
      case 'use-item': state.modal = { kind: 'use-item', title: 'Tend to a companion' }; save(); render(); break;
      case 'heal-spirit': useTonic(id, Boolean(state.battle)); break;
      case 'buy-item': buyItem(target.dataset.item); break;
      case 'restore': {
        const spirit = state.spirits.find((s) => s.id === id);
        if (spirit && !isSoul(spirit) && inventoryCount('balm') > 0 && spirit.contract < 100) {
          state.inventory.balm -= 1; spirit.contract = Math.min(100, spirit.contract + 22);
          note(`A Contract Balm restored ${spirit.name}'s agreement by 22 points.`, '✦'); finishUpdate(`${spirit.name}'s stability rose to ${spirit.contract}.`);
        }
        break;
      }
      case 'reset-save': state.modal = { kind: 'confirm-reset', title: 'A clean page' }; save(); render(); break;
      case 'confirm-reset': try { localStorage.removeItem(SAVE_KEY); } catch { /* Continue with a fresh in-memory journal. */ } state = initialState(); render(); showToast('A new field journal begins.'); break;
      case 'close-modal': state.modal = null; save(); render(); break;
      case 'scrim-close': if (target === document.querySelector('.modal-scrim')) { state.modal = null; save(); render(); } break;
      case 'enter-modal': break;
      case 'use-move': combatTurn(target.dataset.move); break;
      case 'open-switch': state.modal = { kind: 'switch', title: 'Change the active spirit' }; save(); render(); break;
      case 'switch-to': applySwitch(id); break;
      case 'open-heal': state.modal = { kind: 'heal', title: 'Use a Moonwater Tonic' }; save(); render(); break;
      case 'flee': if (state.battle?.type === 'wild') { battleEnd('flee', 'You turned away from the encounter.'); finishUpdate('You left the Spirit Grass.'); } break;
      case 'open-binding': state.modal = { kind: 'binding', title: state.battle?.type === 'reclaim' ? 'Offer a new agreement' : 'A choice of contract' }; save(); render(); break;
      case 'bind': offerBinding(target.dataset.item); break;
      case 'release-wild': releaseWild(); break;
      case 'leave-reclaim': if (state.battle?.type === 'reclaim') state.battle.target.hp = Math.max(1, Math.ceil(maxHp(state.battle.target) * 0.6)); state.battle = null; state.view = 'hall'; finishUpdate('You left the Hall for now.'); break;
      case 'close-battle': state.battle = null; state.view = 'field'; finishUpdate(); break;
      case 'reclaim': setReclaim(id); break;
      case 'replace-move': {
        const modal = state.modal; const spirit = state.spirits.find((s) => s.id === modal?.spiritId);
        if (spirit) { spirit.moves = spirit.moves.map((m) => m === target.dataset.old ? modal.move : m); note(`${spirit.name} learned ${modal.move}, leaving ${target.dataset.old} behind.`, '✦'); }
        state.modal = null; finishUpdate(); break;
      }
      case 'decline-move': {
        if (state.modal) note(`${state.modal.spiritName} kept its familiar moves instead of learning ${state.modal.move}.`, '✦');
        state.modal = null; finishUpdate(); break;
      }
      default: break;
    }
  }

  function goHome() {
    state.modal = null;
    state.view = 'home';
    finishUpdate();
  }

  app.addEventListener('click', (event) => {
    const brand = event.target.closest('.brand-home');
    if (brand) { event.preventDefault(); goHome(); return; }
    const target = event.target.closest('[data-action]');
    if (!target || target.disabled) return;
    if (target.dataset.action === 'scrim-close' && event.target !== target) return;
    handleAction(target.dataset.action, target);
  });
  app.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter' && event.key !== ' ') return;
    const brand = event.target.closest('.brand-home[role="button"]');
    if (brand) { event.preventDefault(); goHome(); return; }
    const target = event.target.closest('.party-card[role="button"]');
    if (target) { event.preventDefault(); handleAction('set-active', target); }
  });

  render();
  save();
})();
