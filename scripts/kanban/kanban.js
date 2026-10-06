/* 看板前端：读取 api/board（或内嵌的快照数据），按来源变化自动重画。无第三方依赖。 */
(() => {
  'use strict';

  const POLL_MS = 2000;
  const STATUS_LABEL = {
    done: '已完成', in_progress: '进行中', open: '待办', blocked: '被阻塞', deferred: '远期', void: '作废',
  };
  const STATUS_ORDER = ['done', 'in_progress', 'open', 'blocked', 'deferred', 'void'];
  const TASK_COLUMNS = [
    { key: 'planned', title: '未入账', hint: '只在 05 任务表里，台账还没有拆出任务' },
    { key: 'todo', title: '已入账待开工', hint: '台账里的拆分任务都还是 todo' },
    { key: 'in_progress', title: '进行中', hint: '有拆分任务在途、只合并了一部分，或只建了表' },
    { key: 'merged', title: '现有拆分都已合并', hint: '台账里已有的拆分都合并了；整项任务有没有做完台账看不出来，要看验收记录' },
    { key: 'later', title: '远期 / 作废', hint: 'P1、未排期与已作废的编号' },
  ];
  const TASK_STATE_LABEL = {
    planned: '未入账', todo: '已入账待开工', in_progress: '进行中', merged: '现有拆分都已合并',
    deferred: '远期 / 未排期', void: '已作废',
  };
  const OPEN_COLUMNS = [
    { key: 'open', title: '待办' },
    { key: 'in_progress', title: '进行中 / 部分已定' },
    { key: 'blocked', title: '等平台验证 / 被阻塞' },
    { key: 'done', title: '已完成 / 已定' },
    { key: 'later', title: '远期 / 作废' },
  ];
  const TABS = [
    { key: 'overview', title: '规划完成度' },
    { key: 'tasks', title: '开发任务看板' },
    { key: 'open', title: '待办与未决' },
    { key: 'caps', title: '平台能力验证' },
    { key: 'list', title: '任务清单' },
  ];

  const state = {
    board: null,
    version: null,
    snapshot: false,
    tab: 'overview',
    lines: new Set(),
    stage: '',
    week: '',
    query: '',
    kinds: new Set(),
    overdueOnly: false,
    showClosed: false,
    openQuery: '',
    sort: { key: 'id', dir: 1 },
    drawer: null,
  };

  const $ = (selector, root = document) => root.querySelector(selector);

  /* 中文输入法拼字期间不重画：重画会换掉输入框，把正在拼的字打断。 */
  let composing = false;
  let pendingRender = false;
  document.addEventListener('compositionstart', () => { composing = true; });
  document.addEventListener('compositionend', (event) => {
    composing = false;
    if (event.target.id === 'task-query') state.query = event.target.value;
    if (event.target.id === 'item-query') state.openQuery = event.target.value;
    pendingRender = false;
    render();
  });

  function el(tag, attrs, ...children) {
    const node = document.createElement(tag);
    for (const [name, value] of Object.entries(attrs || {})) {
      if (value === false || value == null) continue;
      if (name === 'class') node.className = value;
      else if (name === 'dataset') Object.assign(node.dataset, value);
      else if (name.startsWith('on')) node.addEventListener(name.slice(2), value);
      else node.setAttribute(name, value === true ? '' : value);
    }
    for (const child of children.flat()) {
      if (child == null || child === false) continue;
      node.append(child.nodeType ? child : document.createTextNode(String(child)));
    }
    return node;
  }

  /* 只认反引号、加粗、删除线、<br> 与链接文字；其余按纯文本输出，不拼接 HTML。 */
  function md(source) {
    const text = String(source || '');
    const fragment = document.createDocumentFragment();
    const literal = (value) => value.replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
    const pattern = /`([^`]+)`|\*\*((?:[^*`]|`[^`]*`)+)\*\*|~~([^~]+)~~|<br\s*\/?>|\[([^\]]+)\]\([^)]*\)/g;
    let last = 0;
    for (const match of text.matchAll(pattern)) {
      fragment.append(literal(text.slice(last, match.index)));
      if (match[1] != null) fragment.append(el('code', null, literal(match[1])));
      else if (match[2] != null) fragment.append(el('strong', null, md(match[2])));
      else if (match[3] != null) fragment.append(el('s', null, md(match[3])));
      else if (match[4] != null) fragment.append(literal(match[4]));
      else fragment.append(el('br'));
      last = match.index + match[0].length;
    }
    fragment.append(literal(text.slice(last)));
    return fragment;
  }

  const sum = (object) => Object.values(object || {}).reduce((total, value) => total + value, 0);
  const pct = (part, whole) => (whole ? Math.round((part / whole) * 100) : 0);

  function bar(buckets, labels) {
    const total = sum(buckets);
    const node = el('div', { class: 'bar', role: 'img', 'aria-label': legendText(buckets, labels) });
    for (const key of STATUS_ORDER) {
      if (buckets[key]) node.append(el('span', { class: `seg-${key}`, style: `flex:${buckets[key] / total}` }));
    }
    return node;
  }

  function legendText(buckets, labels) {
    return STATUS_ORDER.filter((key) => buckets[key])
      .map((key) => `${(labels && labels[key]) || STATUS_LABEL[key]} ${buckets[key]}`).join('，');
  }

  function legend(buckets, labels) {
    return STATUS_ORDER.filter((key) => buckets[key]).map((key) =>
      el('span', { class: `key ${key}` }, `${(labels && labels[key]) || STATUS_LABEL[key]} `,
        el('span', { class: 'num' }, buckets[key])));
  }

  function sourceText(src) {
    if (!src) return '';
    return src.line ? `${src.file}:${src.line}` : src.file;
  }

  /* ------------------------------------------------------------ 取数与轮询 */
  /* 远端拉取失败时数据可能落后：右上角不再显示成正常的「实时」。 */
  function showFresh() {
    const s = state.board.sources;
    const lag = [s.planning.note, s.ledger.note].filter(Boolean);
    if (lag.length) setLive('stale', `数据可能落后：${lag.join('；')}`);
    else setLive('live', `实时 · 数据更新于 ${stamp(state.board.generated_at)}`);
  }

  function setLive(mode, text) {
    const live = $('#live');
    live.dataset.state = mode;
    $('#live-text').textContent = text;
  }

  function stamp(iso) {
    return iso ? iso.slice(11, 19) : '';
  }

  async function load() {
    const response = await fetch('api/board', { cache: 'no-store' });
    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try { detail = (await response.json()).error || detail; } catch (error) { /* 正文不是 JSON，就用状态码 */ }
      throw Object.assign(new Error(detail), { served: true });
    }
    apply(await response.json());
  }

  function problem(error) {
    return error.served
      ? `看板服务在运行，但读取来源时出错（${error.message}）；页面停在上次读到的数据`
      : '连接已断开：看板服务没有在运行，页面停在上次读到的数据';
  }

  function apply(board) {
    const first = !state.board;
    state.board = board;
    state.version = board.version;
    // 浏览器里记住的筛选可能指向已经不存在的线、阶段或周次；留着会筛成空白却显示成「全部」。
    state.lines = new Set([...state.lines].filter((key) => board.lines.some((line) => line.id === key)));
    state.kinds = new Set([...state.kinds].filter((key) => board.item_kinds.some((kind) => kind.key === key)));
    if (!board.stages.some((stage) => stage.id === state.stage)) state.stage = '';
    if (!board.calendar.weeks.some((week) => week.id === state.week)) state.week = '';
    if (composing) { pendingRender = true; return; }
    render();
    if (!first) toast(`来源有变化，已更新（${stamp(board.generated_at)}）`);
  }

  async function tick() {
    if (document.hidden) return;
    try {
      const response = await fetch('api/version', { cache: 'no-store' });
      const { version, fetched_at: fetched } = await response.json();
      if (version !== state.version) await load();
      state.fetched = fetched;
      const cell = $('#fetched-at');
      if (cell) cell.textContent = fetched ? `上次向远端核对 ${fetched}` : '还没有向远端核对过';
      showFresh();
    } catch (error) {
      if (!state.board) $('#main').replaceChildren(el('div', { class: 'notice error' }, problem(error)));
      setLive('stale', problem(error));
    }
  }

  let toastTimer = 0;
  function toast(text) {
    const node = $('#toast');
    node.textContent = text;
    node.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { node.hidden = true; }, 2600);
  }

  /* ------------------------------------------------------------ 页面骨架 */
  function saveView() {
    try {
      localStorage.setItem('couli-kanban-view', JSON.stringify({
        tab: state.tab, lines: [...state.lines], stage: state.stage, week: state.week,
        kinds: [...state.kinds], showClosed: state.showClosed,
      }));
    } catch (error) { /* 无痕窗口等场景下不保存，功能不受影响 */ }
  }

  function restoreView() {
    try {
      const saved = JSON.parse(localStorage.getItem('couli-kanban-view') || '{}');
      if (TABS.some((tab) => tab.key === saved.tab)) state.tab = saved.tab;
      state.lines = new Set(saved.lines || []);
      state.kinds = new Set(saved.kinds || []);
      state.stage = saved.stage || '';
      state.week = saved.week || '';
      state.showClosed = Boolean(saved.showClosed);
    } catch (error) { /* 同上 */ }
    const hash = location.hash.slice(1);
    if (TABS.some((tab) => tab.key === hash)) state.tab = hash;
  }

  function render() {
    const board = state.board;
    const main = $('#main');
    const keep = {
      x: window.scrollX,
      y: window.scrollY,
      cols: [...document.querySelectorAll('[data-scroll]')].map((node) => [node.dataset.scroll, node.scrollTop, node.scrollLeft]),
      focus: document.activeElement && document.activeElement.id,
      caret: document.activeElement && document.activeElement.selectionStart,
      drawerTop: $('.drawer') ? $('.drawer').scrollTop : 0,
      inDrawer: Boolean(document.activeElement && document.activeElement.closest('.drawer')),
    };

    $('#subtitle').textContent = `今天 ${board.today}（${board.calendar.current_week || '周计划之外'}）· ${board.tasks.length} 个计划任务 · ${
      board.sources.ledger.available ? `台账 ${board.ledger.entries.length} 个拆分任务` : '读不到工程台账'}`;
    renderTabs();
    document.documentElement.style.setProperty('--topbar-h', `${$('.topbar').offsetHeight}px`);
    main.replaceChildren(...notices(board), ...({
      overview: viewOverview, tasks: viewTasks, open: viewOpen, caps: viewCaps, list: viewList,
    })[state.tab](board));
    renderSources(board);
    renderDrawer();

    for (const [key, top, left] of keep.cols) {
      const node = document.querySelector(`[data-scroll="${key}"]`);
      if (node) { node.scrollTop = top; node.scrollLeft = left; }
    }
    window.scrollTo(keep.x, keep.y);
    const drawer = $('.drawer');
    if (drawer) {
      drawer.scrollTop = keep.drawerTop;
      if (keep.inDrawer && !keep.focus) $('.drawer .close').focus({ preventScroll: true });
    }
    if (keep.focus) {
      const node = document.getElementById(keep.focus);
      if (node) {
        node.focus({ preventScroll: true });
        if (keep.caret != null && node.setSelectionRange) node.setSelectionRange(keep.caret, keep.caret);
      }
    }
  }

  function renderTabs() {
    const board = state.board;
    const counts = {
      tasks: board.tasks.length,
      open: board.open_items.filter((item) => ['open', 'in_progress', 'blocked'].includes(item.status)).length,
      caps: board.caps.items.length,
    };
    $('#tabs').replaceChildren(...TABS.map((tab) => el('button', {
      class: 'tab', role: 'tab', id: `tab-${tab.key}`, 'aria-selected': String(state.tab === tab.key),
      onclick: () => { state.tab = tab.key; history.replaceState(null, '', `#${tab.key}`); saveView(); window.scrollTo(0, 0); render(); },
    }, tab.title, counts[tab.key] != null ? el('span', { class: 'count num' }, counts[tab.key]) : null)));
  }

  function notices(board) {
    const list = [...(board.warnings || [])];
    if (!board.sources.ledger.available) list.push('没有读到工程台账（找不到代码仓库或它的主干）：下面任务的开发状态是未知，不是「未入账」。');
    if (!board.sources.runs.available) list.push('没有找到运行目录：看不到哪些任务正在进行，在途的任务会显示成「已入账待开工」。');
    const notes = (board.notes || []).filter((text) => !text.startsWith('没有读到工程台账'));
    return [
      list.length ? el('div', { class: 'notice' }, el('strong', null, '读取时发现的问题（相应数字可能不全）'),
        el('ul', null, list.map((text) => el('li', null, text)))) : null,
      notes.length ? el('details', { class: 'notice quiet' }, el('summary', null, `${notes.length} 条提示（没能归类的状态按待办计，少格的行按空白计）`),
        el('ul', null, notes.map((text) => el('li', null, text)))) : null,
    ].filter(Boolean);
  }

  function renderSources(board) {
    const s = board.sources;
    const commit = (source) => `${source.ref} @ ${source.sha}（提交于 ${source.committed_at}）${source.note ? ` · ${source.note}` : ''}`;
    const rows = [
      ['规划文档', s.planning.mode === 'git'
        ? `规划仓库 ${commit(s.planning)}`
        : `本机文件 ${s.planning.root} · ${s.planning.branch || ''} @ ${s.planning.sha || '未知提交'}${s.planning.dirty ? ' · 有未提交改动' : ''}（没有合并的改动也会显示）`],
      ['工程台账', s.ledger.available ? `${s.ledger.repo} · ${commit(s.ledger)}`
        : `没有找到代码仓库（${s.ledger.repo}）；任务只显示规划，开发状态未知`],
      ['在途状态', s.runs.available ? s.runs.dir : `没有找到运行目录（${s.runs.dir}）；看不到哪些任务正在进行`],
      ['生成时间', `${board.generated_at}${state.snapshot ? '（静态快照，不会自动更新）' : ''}`],
    ];
    if (s.spec_ref && s.spec_ref.sha) {
      rows.splice(2, 0, ['代码依据的规划版本', `SPEC_REF ${s.spec_ref.sha}${s.spec_ref.behind ? `，比这里读到的规划旧 ${s.spec_ref.behind} 个提交` : ''}`]);
    }
    const list = el('dl', null, rows.flatMap(([name, text]) => [el('dt', null, name), el('dd', null, text)]));
    if (!state.snapshot) {
      list.append(el('dt', null, '远端核对'), el('dd', { id: 'fetched-at' }, state.fetched ? `上次向远端核对 ${state.fetched}` : '还没有向远端核对过'));
    }
    $('#sources').replaceChildren(list);
  }

  /* ------------------------------------------------------------ 规划完成度 */
  function viewOverview(board) {
    const p = board.planning;
    const tiles = el('div', { class: 'tiles' }, p.headline.map((tile) => el('div', { class: 'tile' },
      el('div', { class: 'label' }, tile.label),
      el('div', { class: 'value num' }, tile.value, tile.unit ? el('small', null, tile.unit) : null),
      el('div', { class: 'hint' }, tile.hint))));

    const dims = el('section', { class: 'panel' },
      el('h2', null, '规划阶段完成度'),
      el('p', { class: 'lede' }, p.lede),
      el('div', { class: 'dims' }, p.dimensions.map((dim) => el('div', { class: 'dim' },
        el('div', { class: 'dim-title' }, dim.title, el('small', null, dim.source)),
        bar(dim.buckets, dim.labels),
        el('div', { class: 'dim-pct num' }, dim.pct == null ? '—' : `${dim.pct}%`),
        el('div', { class: 'dim-legend' }, legend(dim.buckets, dim.labels),
          dim.note ? el('span', { class: 'note' }, dim.note) : null)))));

    const stones = el('section', { class: 'panel' },
      el('h2', null, '里程碑'),
      el('p', { class: 'lede' }, board.calendar.note),
      el('div', { class: 'timeline' }, board.calendar.milestones.map((stone) => el('div', { class: 'stone', dataset: { when: stone.when_state } },
        el('div', { class: 'id' }, `${stone.id} ${stone.name}`),
        el('div', { class: 'date' }, stone.when),
        el('div', { class: 'exit', title: stone.exit }, md(stone.exit))))));

    const lines = el('section', { class: 'panel' },
      el('h2', null, '各线开发任务'),
      el('p', { class: 'lede' }, '按 05 任务表的各条线统计，右边是已经动工（台账里有拆分任务）的任务数。台账看不出一项任务有没有做完：「现有拆分都已合并」只说明已有的拆分合并了，完成与否要看验收记录。'),
      el('div', { class: 'dims' }, board.lines.map((line) => el('div', { class: 'dim' },
        el('div', { class: 'dim-title' }, `${line.id} ${line.name}`, el('small', null, `${line.total} 个任务`)),
        taskBar(line.states),
        el('div', { class: 'dim-pct num', title: '已动工 / 任务总数' }, `${line.started}/${line.total}`),
        el('div', { class: 'dim-legend' }, taskLegend(line.states))))));

    const stages = el('section', { class: 'panel' },
      el('h2', null, '阶段 S0–S4'),
      el('p', { class: 'lede' }, '阶段按用户能否走完一条流程判定，按平台分别出门（05 §0、10 §1）。右边同样是已动工的任务数，不是出门进度。'),
      el('div', { class: 'dims' }, board.stages.map((stage) => el('div', { class: 'dim' },
        el('div', { class: 'dim-title' }, stage.id, el('small', null, `${stage.name} · ${stage.weeks}`)),
        taskBar(stage.states),
        el('div', { class: 'dim-pct num', title: '已动工 / 任务总数' }, `${stage.started}/${stage.total}`),
        el('div', { class: 'dim-legend' }, taskLegend(stage.states),
          el('span', { class: 'note' }, md(stage.result)))))));

    const jump = (kind) => { state.kinds = new Set([kind]); state.tab = 'open'; history.replaceState(null, '', '#open'); saveView(); window.scrollTo(0, 0); render(); };
    const focus = el('section', { class: 'panel' },
      el('h2', null, '未决事项分布'),
      el('p', { class: 'lede' }, `各类事项现在的状态，点一行看明细。${p.untracked ? `其中 ${p.untracked} 条所在的表没有状态列（06 的数据、法务文本、外部答复、硬件几节），暂按待办计；06 写明负责人称账号资质与法务文本已基本完成，只是没有逐项标记。` : ''}`),
      el('div', { class: 'table-wrap' }, el('table', { class: 'list' },
        el('thead', null, el('tr', null, ['类别', '待办', '进行中', '等平台验证 / 被阻塞', '已完成', '远期或作废'].map((name) => el('th', null, name)))),
        el('tbody', null, board.item_kinds.map((kind) => {
          const count = (...statuses) => board.open_items.filter((item) => item.kind === kind.key && statuses.includes(item.status)).length;
          return el('tr', { onclick: () => jump(kind.key) },
            el('td', null, el('button', { class: 'linklike', type: 'button' }, kind.label)),
            el('td', { class: 'num' }, count('open')), el('td', { class: 'num' }, count('in_progress')),
            el('td', { class: 'num' }, count('blocked')), el('td', { class: 'num' }, count('done')),
            el('td', { class: 'num' }, count('deferred', 'void')));
        })))));

    return [tiles, dims, stones, lines, stages, focus];
  }

  const TASK_BUCKET = { merged: 'merged', in_progress: 'in_progress', todo: 'open', planned: 'open', deferred: 'deferred', void: 'void' };

  function taskBar(states) {
    const total = sum(states);
    const node = el('div', { class: 'bar', role: 'img', 'aria-label': taskLegendText(states) });
    for (const key of ['merged', 'in_progress', 'todo', 'planned', 'deferred', 'void']) {
      if (!states[key]) continue;
      const span = el('span', { class: `seg-${TASK_BUCKET[key]}`, style: `flex:${states[key] / total}` });
      if (key === 'planned') span.style.opacity = '0.4';
      node.append(span);
    }
    return node;
  }

  function taskLegendText(states) {
    return Object.keys(TASK_STATE_LABEL).filter((key) => states[key]).map((key) => `${TASK_STATE_LABEL[key]} ${states[key]}`).join('，');
  }

  function taskLegend(states) {
    return ['merged', 'in_progress', 'todo', 'planned', 'deferred', 'void'].filter((key) => states[key]).map((key) => {
      const node = el('span', { class: `key ${TASK_BUCKET[key]}` }, `${TASK_STATE_LABEL[key]} `, el('span', { class: 'num' }, states[key]));
      if (key === 'planned') node.style.opacity = '0.75';
      return node;
    });
  }

  /* ------------------------------------------------------------ 开发任务 */
  function taskMatches(task) {
    if (state.lines.size && !state.lines.has(task.line)) return false;
    if (state.stage && !task.stages.includes(state.stage)) return false;
    if (state.week && !task.weeks.includes(state.week)) return false;
    if (state.query) {
      const hay = `${task.id} ${task.content} ${task.when} ${task.refs} ${task.extra} ${task.deps_raw} ${task.share} ${task.ledger.map((entry) => `${entry.id} ${entry.title}`).join(' ')}`.toLowerCase();
      if (!state.query.toLowerCase().split(/\s+/).every((word) => hay.includes(word))) return false;
    }
    return true;
  }

  function taskFilters(board, shown) {
    const chip = (key, label) => el('button', {
      class: 'chip', type: 'button', 'aria-pressed': String(key ? state.lines.has(key) : !state.lines.size),
      onclick: () => {
        if (!key) state.lines.clear(); else if (state.lines.has(key)) state.lines.delete(key); else state.lines.add(key);
        saveView(); render();
      },
    }, label);
    const select = (id, label, value, options, assign) => el('select', {
      id, 'aria-label': label, onchange: (event) => { assign(event.target.value); saveView(); render(); },
    }, el('option', { value: '' }, label), options.map(([key, text]) => el('option', { value: key, selected: key === value }, text)));

    return el('div', { class: 'filters' },
      el('input', {
        type: 'search', id: 'task-query', placeholder: '搜编号、内容、BR / AC 编号', 'aria-label': '搜索任务', value: state.query,
        oninput: (event) => { state.query = event.target.value; if (!event.isComposing) render(); },
      }),
      el('div', { class: 'chips', role: 'group', 'aria-label': '按线筛选' }, chip('', '全部'),
        board.lines.map((line) => chip(line.id, `${line.id} ${line.total}`))),
      select('task-stage', '全部阶段', state.stage, board.stages.map((stage) => [stage.id, `${stage.id} ${stage.name}`]), (value) => { state.stage = value; }),
      select('task-week', '全部周次', state.week, board.calendar.weeks.map((week) => [week.id, `${week.id}（${week.range}）`]), (value) => { state.week = value; }),
      el('span', { class: 'summary num' }, `显示 ${shown} / ${board.tasks.length}`));
  }

  function taskColumn(task) {
    return task.state === 'void' || task.state === 'deferred' ? 'later' : task.state;
  }

  function taskCard(task) {
    return el('button', { class: 'card', type: 'button', onclick: () => openDrawer('task', task.id) },
      el('div', { class: 'card-top' },
        el('span', { class: 'card-id num' }, task.id),
        task.state === 'void' ? el('span', { class: 'tag' }, '已作废') : null,
        task.behind ? el('span', { class: 'tag warn', title: '05 里写的计划周已过，台账里还没有合并完' }, '已过计划周') : null,
        el('span', { class: 'tag line' }, task.line)),
      el('div', { class: 'card-title' }, task.title),
      el('div', { class: 'card-meta' },
        task.when ? el('span', { class: 'tag' }, task.when_short) : null,
        task.stages.map((stage) => el('span', { class: 'tag' }, stage)),
        task.human_deps.length && !['deferred', 'void'].includes(task.state)
          ? el('span', { class: 'tag', title: task.human_deps.join('；') }, '有人工前置') : null),
      task.ledger.length ? el('div', { class: 'subs' }, task.ledger.map((entry) => el('span', {
        class: `sub ${entry.state}`, title: `${entry.id} · ${entry.state_label}${entry.pr ? ` · PR #${entry.pr}` : ''}\n${entry.title}`,
      }, entry.id.slice(task.id.length) || '整项', entry.state === 'done' ? ' ✓' : entry.state === 'in_progress' ? ' ●' : ''))) : null);
  }

  function viewTasks(board) {
    const tasks = board.tasks.filter(taskMatches);
    const known = board.sources.ledger.available;
    return [
      taskFilters(board, tasks.length),
      el('div', { class: 'board', dataset: { scroll: 'task-board' } }, TASK_COLUMNS.map((column) => {
        const cards = tasks.filter((task) => taskColumn(task) === column.key);
        const unknown = !known && column.key === 'planned';
        return el('section', { class: 'col' },
          el('div', { class: 'col-head' },
            el('h3', null, unknown ? '开发状态未知' : column.title, el('span', { class: 'count num' }, cards.length)),
            el('p', null, unknown ? '没有读到工程台账，只知道这些任务在 05 的计划里' : column.hint)),
          el('div', { class: 'col-body', dataset: { scroll: `task-${column.key}` } },
            cards.length ? cards.map(taskCard) : el('div', { class: 'col-empty' }, '没有任务')));
      })),
    ];
  }

  /* ------------------------------------------------------------ 待办与未决 */
  function itemMatches(item) {
    if (state.kinds.size && !state.kinds.has(item.kind)) return false;
    if (state.overdueOnly && !item.overdue) return false;
    if (state.openQuery) {
      const hay = `${item.id} ${item.title} ${item.group} ${item.status_raw} ${item.owner} ${item.due} ${item.fields.map((pair) => pair[1]).join(' ')}`.toLowerCase();
      if (!state.openQuery.toLowerCase().split(/\s+/).every((word) => hay.includes(word))) return false;
    }
    return true;
  }

  function itemCard(item) {
    return el('button', { class: 'card', type: 'button', onclick: () => openDrawer('item', item.id) },
      el('div', { class: 'card-top' },
        el('span', { class: 'card-id num' }, item.id),
        item.overdue ? el('span', { class: 'tag warn' }, '已过截止') : null,
        item.tracked ? null : el('span', { class: 'tag' }, '未登记状态'),
        el('span', { class: 'tag line' }, item.kind_label)),
      el('div', { class: 'card-title' }, md(item.title)),
      el('div', { class: 'card-meta' },
        item.due ? el('span', { class: 'tag' }, `截止 ${item.due_short || item.due}`) : null,
        item.owner ? el('span', { class: 'tag' }, item.owner) : null,
        item.same_as ? el('span', { class: 'tag', title: '06 与 08 各登记了一行，是同一个决定' }, `同 ${item.same_as}`) : null));
  }

  const itemColumn = (item) => (['deferred', 'void'].includes(item.status) ? 'later' : item.status);

  function viewOpen(board) {
    const kinds = board.item_kinds;
    const items = board.open_items.filter(itemMatches);
    const columns = state.showClosed ? OPEN_COLUMNS : OPEN_COLUMNS.filter((column) => !['done', 'later'].includes(column.key));
    const chip = (key, label) => el('button', {
      class: 'chip', type: 'button', 'aria-pressed': String(key ? state.kinds.has(key) : !state.kinds.size),
      onclick: () => {
        if (!key) state.kinds.clear(); else if (state.kinds.has(key)) state.kinds.delete(key); else state.kinds.add(key);
        saveView(); render();
      },
    }, label);
    const toggle = (id, label, checked, assign) => el('label', null, el('input', {
      type: 'checkbox', id, checked, onchange: (event) => { assign(event.target.checked); saveView(); render(); },
    }), ` ${label}`);

    return [
      el('div', { class: 'filters' },
        el('input', {
          type: 'search', id: 'item-query', placeholder: '搜编号或事项', 'aria-label': '搜索事项', value: state.openQuery,
          oninput: (event) => { state.openQuery = event.target.value; if (!event.isComposing) render(); },
        }),
        el('div', { class: 'chips', role: 'group', 'aria-label': '按类别筛选' }, chip('', '全部'),
          kinds.map((kind) => chip(kind.key, `${kind.label} ${kind.open}`))),
        toggle('item-overdue', '只看已过截止', state.overdueOnly, (value) => { state.overdueOnly = value; }),
        toggle('item-closed', '显示已完成与作废', state.showClosed, (value) => { state.showClosed = value; }),
        el('span', { class: 'summary num' }, `显示 ${items.filter((item) => columns.some((column) => column.key === itemColumn(item))).length} / ${board.open_items.length}`)),
      el('div', { class: 'board', dataset: { scroll: 'open-board' } }, columns.map((column) => {
        const cards = items.filter((item) => itemColumn(item) === column.key);
        return el('section', { class: 'col' },
          el('div', { class: 'col-head' }, el('h3', null, column.title, el('span', { class: 'count num' }, cards.length))),
          el('div', { class: 'col-body', dataset: { scroll: `open-${column.key}` } },
            cards.length ? cards.map(itemCard) : el('div', { class: 'col-empty' }, '没有条目')));
      })),
    ];
  }

  /* ------------------------------------------------------------ 平台能力验证 */
  function viewCaps(board) {
    const caps = board.caps;
    const pill = (item) => el('button', {
      class: `tag ${item.status === 'open' ? '' : item.status} cap`, type: 'button', title: `${item.id} ${item.short}`,
      onclick: () => openDrawer('cap', item.id),
    }, item.status === 'deferred' ? `${item.status_raw}（后续）` : item.status_raw);
    const shared = caps.platforms.filter((platform) => caps.matrix.includes(platform.id));
    const numbers = Object.keys(caps.names).sort();
    const own = caps.items.filter((cap) => !caps.matrix.includes(cap.platform));

    const summary = el('section', { class: 'panel' },
      el('h2', null, '各平台能力验证状态'),
      el('p', { class: 'lede' }, caps.note),
      el('div', { class: 'dims' }, caps.platforms.map((platform) => el('div', { class: 'dim' },
        el('div', { class: 'dim-title' }, platform.name, el('small', null, `${platform.total} 条能力`)),
        bar(platform.buckets, caps.labels),
        el('div', { class: 'dim-pct num' }, `${platform.buckets.done || 0}/${platform.total}`),
        el('div', { class: 'dim-legend' }, legend(platform.buckets, caps.labels))))));

    const matrix = el('section', { class: 'panel' },
      el('h2', null, '淘宝、京东、拼多多、美团（同号同义）'),
      el('p', { class: 'lede' }, '点状态看这条能力的接口、实验、通过标准和降级做法。'),
      el('div', { class: 'table-wrap' }, el('table', { class: 'list matrix' },
        el('thead', null, el('tr', null, el('th', null, '能力'), shared.map((platform) => el('th', null, platform.name)))),
        el('tbody', null, numbers.map((number) => el('tr', null,
          el('td', null, `${number} ${caps.names[number]}`),
          shared.map((platform) => {
            const item = caps.items.find((cap) => cap.platform === platform.id && cap.number === number);
            return el('td', null, item ? pill(item) : '—');
          })))))));

    const cross = el('section', { class: 'panel' },
      el('h2', null, `跨平台与系统能力（${own.length} 条）`),
      el('div', { class: 'table-wrap' }, el('table', { class: 'list matrix' },
        el('thead', null, el('tr', null, ['编号', '能力', '状态', '谁做', '截止'].map((name) => el('th', null, name)))),
        el('tbody', null, own.map((cap) => el('tr', null,
          el('td', { class: 'nowrap num' }, cap.id), el('td', { class: 'wide' }, md(cap.title)),
          el('td', { class: 'nowrap' }, pill(cap)), el('td', { class: 'nowrap' }, cap.owner), el('td', null, cap.due)))))));

    const plan = el('section', { class: 'panel' },
      el('h2', null, `验证计划（${caps.vtasks.length} 项）`),
      el('p', { class: 'lede' }, caps.vnote),
      el('div', { class: 'table-wrap' }, el('table', { class: 'list' },
        el('thead', null, el('tr', null, ['编号', '计划周', '任务', '能力', '谁做', '阻塞阶段'].map((name) => el('th', null, name)))),
        el('tbody', null, caps.vtasks.map((task) => el('tr', { onclick: () => openDrawer('vtask', task.id) },
          el('td', { class: 'nowrap num' }, task.id), el('td', { class: 'nowrap' }, task.week),
          el('td', { class: 'wide' }, md(task.title)), el('td', null, task.caps),
          el('td', { class: 'nowrap' }, task.owner), el('td', null, task.blocks)))))));

    return [summary, matrix, cross, plan];
  }

  /* ------------------------------------------------------------ 任务清单 */
  const LIST_COLUMNS = [
    { key: 'id', title: '编号', get: (task) => task.order },
    { key: 'line', title: '线', get: (task) => task.line },
    { key: 'title', title: '内容', get: (task) => task.title },
    { key: 'when', title: '计划', get: (task) => task.week_rank },
    { key: 'stages', title: '阶段', get: (task) => task.stages.join(' ') },
    { key: 'state', title: '状态', get: (task) => Object.keys(TASK_STATE_LABEL).indexOf(task.state) },
    { key: 'ledger', title: '台账拆分（已合并 / 已拆）', get: (task) => task.ledger.length },
    { key: 'deps', title: '依赖', get: (task) => task.deps.join(' ') },
  ];

  function downloadCsv(tasks) {
    const quote = (value) => `"${String(value == null ? '' : value).replace(/"/g, '""')}"`;
    const rows = [['编号', '线', '承担的线', '内容', '计划', '阶段', '状态', '已合并拆分', '已拆分', '拆分任务', 'PR', '依赖', '关联', '出处']];
    for (const task of tasks) {
      rows.push([task.id, task.line, task.share, task.content, task.when, task.stages.join(' '), TASK_STATE_LABEL[task.state],
        task.ledger.filter((entry) => entry.state === 'done').length, task.ledger.length,
        task.ledger.map((entry) => `${entry.id}:${entry.state_label}`).join(' '),
        task.ledger.filter((entry) => entry.pr).map((entry) => `#${entry.pr}`).join(' '),
        task.deps_raw, task.refs, sourceText(task.src)]);
    }
    const blob = new Blob(['﻿' + rows.map((row) => row.map(quote).join(',')).join('\r\n')], { type: 'text/csv;charset=utf-8' });
    const link = el('a', { href: URL.createObjectURL(blob), download: `couli-tasks-${state.board.today}.csv` });
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  }

  function viewList(board) {
    const column = LIST_COLUMNS.find((item) => item.key === state.sort.key) || LIST_COLUMNS[0];
    const tasks = board.tasks.filter(taskMatches).sort((a, b) => {
      const left = column.get(a);
      const right = column.get(b);
      const order = typeof left === 'number' ? left - right : String(left).localeCompare(String(right), 'zh-CN', { numeric: true });
      return (order || a.order - b.order) * state.sort.dir;
    });
    const filters = taskFilters(board, tasks.length);
    filters.append(el('button', { class: 'chip', type: 'button', onclick: () => downloadCsv(tasks) }, '导出 CSV'));

    return [filters, el('div', { class: 'table-wrap tall', dataset: { scroll: 'task-list' } }, el('table', { class: 'list' },
      el('thead', null, el('tr', null, LIST_COLUMNS.map((item) => el('th', {
        'aria-sort': state.sort.key === item.key ? (state.sort.dir > 0 ? 'ascending' : 'descending') : null,
      }, el('button', {
        type: 'button',
        onclick: () => { state.sort = { key: item.key, dir: state.sort.key === item.key ? -state.sort.dir : 1 }; render(); },
      }, item.title, state.sort.key === item.key ? (state.sort.dir > 0 ? ' ▲' : ' ▼') : ''))))),
      el('tbody', null, tasks.map((task) => el('tr', { onclick: () => openDrawer('task', task.id) },
        el('td', { class: 'nowrap num' }, task.id),
        el('td', null, task.line),
        el('td', { class: 'wide' }, task.title),
        el('td', { class: 'nowrap' }, task.when_short),
        el('td', { class: 'nowrap' }, task.stages.join(' ')),
        el('td', { class: 'nowrap' }, el('span', { class: `tag ${{ merged: 'done', in_progress: 'in_progress' }[task.state] || ''}` }, TASK_STATE_LABEL[task.state])),
        el('td', { class: 'nowrap num' }, task.ledger.length ? `${task.ledger.filter((entry) => entry.state === 'done').length} / ${task.ledger.length}` : '—'),
        el('td', null, task.deps.join('、'))))))) ];
  }

  /* ------------------------------------------------------------ 详情抽屉 */
  function openDrawer(kind, id) {
    state.drawer = { kind, id, opener: document.activeElement };
    renderDrawer();
    const close = $('.drawer .close');
    if (close) close.focus();
  }

  function closeDrawer() {
    const opener = state.drawer && state.drawer.opener;
    state.drawer = null;
    renderDrawer();
    if (opener && opener.isConnected) opener.focus();
  }

  function field(title, body) {
    if (body == null || body === '' || (Array.isArray(body) && !body.length)) return [];
    if (body.nodeType && ['', '—', '-'].includes(body.textContent.trim())) return [];
    return [el('h3', null, title), el('p', null, body)];
  }

  function taskLink(id) {
    return el('button', { class: 'linklike', type: 'button', onclick: () => openDrawer('task', id) }, id);
  }

  function drawerTask(board, task) {
    const dependents = board.tasks.filter((other) => other.deps.includes(task.id));
    const web = board.sources.ledger.web_url;
    return [
      el('p', { class: 'path' }, `${task.line} · ${TASK_STATE_LABEL[task.state]}`),
      ...field('内容', md(task.content)),
      ...field('计划时间', task.when),
      ...field('由哪条线承担', task.share),
      ...field('阶段', task.stages.join('、')),
      ...field('为什么算进行中', task.note),
      ...field('依赖', task.deps_raw ? md(task.deps_raw) : null),
      ...(task.deps.length ? [el('p', null, '打开依赖任务：', task.deps.flatMap((id, index) => [index ? '、' : '', taskLink(id)]))] : []),
      ...(dependents.length ? [el('h3', null, '被这些任务依赖'), el('p', null, dependents.flatMap((other, index) => [index ? '、' : '', taskLink(other.id)]))] : []),
      ...field('关联的规则与验收编号', task.refs ? md(task.refs) : null),
      ...field(task.extra_label || '验收 / 产出', task.extra ? md(task.extra) : null),
      el('h3', null, `工程台账里的拆分任务（${task.ledger.length}）`),
      task.ledger.length ? el('ul', null, task.ledger.map((entry) => el('li', null,
        el('strong', null, entry.id), ` · ${entry.state_label}`,
        entry.pr && web ? [' · ', el('a', { href: `${web}/pull/${entry.pr}`, target: '_blank', rel: 'noopener' }, `PR #${entry.pr}`)] : null,
        entry.step ? ` · ${entry.step}` : null,
        el('br'), md(entry.title))))
        : el('p', null, '台账里还没有从这项任务拆出的条目。'),
      el('h3', null, '出处'), el('p', { class: 'path' }, sourceText(task.src)),
    ];
  }

  function drawerItem(item) {
    return [
      el('p', { class: 'path' }, `${item.kind_label} · ${item.group}`),
      ...field('事项', md(item.title)),
      ...field(item.status_quoted ? '状态（文档原文）' : '状态（看板归纳，文档里这张表没有状态栏）', md(item.status_raw)),
      ...field('截止', item.due ? md(item.due) : null),
      ...field('谁处理', item.owner),
      ...(item.fields || []).flatMap(([name, text]) => field(name, md(text))),
      el('h3', null, '出处'), el('p', { class: 'path' }, sourceText(item.src)),
    ];
  }

  function renderDrawer() {
    const root = $('#drawer-root');
    const board = state.board;
    if (!state.drawer || !board) { root.replaceChildren(); return; }
    const { kind, id } = state.drawer;
    let title = id;
    let body = [];
    if (kind === 'task') {
      const task = board.tasks.find((item) => item.id === id);
      if (task) body = drawerTask(board, task);
    } else if (kind === 'item') {
      const item = board.open_items.find((entry) => entry.id === id);
      if (item) body = drawerItem(item);
    } else if (kind === 'cap') {
      const cap = board.caps.items.find((entry) => entry.id === id);
      if (cap) body = drawerItem({ ...cap, kind_label: '平台能力', group: cap.platform_name, status_quoted: true });
    } else if (kind === 'vtask') {
      const task = board.caps.vtasks.find((entry) => entry.id === id);
      if (task) body = drawerItem({ ...task, kind_label: '验证计划', group: task.week, status_raw: task.done_mark, fields: task.fields });
    }
    if (!body.length) { state.drawer = null; root.replaceChildren(); return; }
    root.replaceChildren(
      el('div', { class: 'drawer-backdrop', onclick: closeDrawer }),
      el('aside', { class: 'drawer', role: 'dialog', 'aria-modal': 'true', 'aria-labelledby': 'drawer-title' },
        el('header', null, el('h2', { id: 'drawer-title' }, title),
          el('button', { class: 'close', type: 'button', 'aria-label': '关闭', onclick: closeDrawer }, '✕')),
        body));
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && state.drawer) closeDrawer();
  });

  window.addEventListener('resize', () => {
    document.documentElement.style.setProperty('--topbar-h', `${$('.topbar').offsetHeight}px`);
  });

  window.addEventListener('hashchange', () => {
    const hash = location.hash.slice(1);
    if (state.board && hash !== state.tab && TABS.some((tab) => tab.key === hash)) { state.tab = hash; render(); }
  });

  /* ------------------------------------------------------------ 启动 */
  async function start() {
    restoreView();
    const embedded = $('#board-data').textContent.trim();
    if (embedded) {
      state.snapshot = true;
      apply(JSON.parse(embedded));
      setLive('snapshot', `静态快照 · 生成于 ${state.board.generated_at.slice(0, 19).replace('T', ' ')}`);
      return;
    }
    try {
      await load();
      showFresh();
    } catch (error) {
      $('#main').replaceChildren(el('div', { class: 'notice error' }, problem(error)));
      setLive('stale', problem(error));
    }
    setInterval(tick, POLL_MS);
    document.addEventListener('visibilitychange', tick);
  }

  start();
})();
