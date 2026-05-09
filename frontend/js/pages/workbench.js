/**
 * workbench.js — Operator-first connected workbench
 * SRP: page composition and local interaction state only.
 */

import { navigate } from '../router.js';
import { state } from '../state.js';

const PROJECTS = [
  {
    id: 'terminal-2',
    name: 'Terminal 2 Core Package',
    client: 'Heathrow retrofit',
    phase: 'Pre-issue review',
    docs: 184,
    chunks: 48220,
    healthy: 4,
    blockers: 3,
    writebacks: 2,
    coverage: '96%',
    owner: 'VDC lead',
    release: 'IFC-A2 issue set',
    deadline: 'Owner review at 16:30 IST',
  },
  {
    id: 'hospital-west',
    name: 'Hospital West Wing MEP',
    client: 'Bengaluru care campus',
    phase: 'Field answer prep',
    docs: 126,
    chunks: 31890,
    healthy: 3,
    blockers: 1,
    writebacks: 1,
    coverage: '91%',
    owner: 'Design coordination',
    release: 'RFI response pack',
    deadline: 'Site query window closes at 18:00 IST',
  },
  {
    id: 'pod-4',
    name: 'Data Centre Pod 4',
    client: 'Edge campus expansion',
    phase: 'Connector mapping',
    docs: 92,
    chunks: 22410,
    healthy: 2,
    blockers: 2,
    writebacks: 0,
    coverage: '88%',
    owner: 'Document control',
    release: 'Coordination delta package',
    deadline: 'Model coordination tomorrow 09:00 IST',
  },
];

const CONNECTOR_ORDER = ['acc', 'procore', 'sharepoint', 'revit'];

const CONNECTORS = {
  acc: {
    name: 'Autodesk Construction Cloud',
    short: 'ACC',
    icon: 'fa-building',
    tone: 'pass',
    surface: 'Sheets, published PDFs, issue metadata',
    summary: '42 sheets mapped | 11 RFIs linked | append-only issue writeback',
    status: 'Healthy',
    statusMeta: 'Delta sync every 2 minutes',
    scope: 'Published drawing set + transmittals',
    writeback: 'Issue cards, contradiction summaries, source links',
    policy: 'No destructive writes; note-only updates',
    owner: 'Service account scoped to one project',
    nextSync: 'Next full sweep at 16:30 IST',
    recent: [
      { time: '15:12', text: '2 contradiction cards pushed to ACC issue log.' },
      { time: '14:56', text: 'A-221 revision detected and queued for re-scan.' },
      { time: '14:41', text: 'Owner response thread linked to sheet A-118.' },
    ],
  },
  procore: {
    name: 'Procore',
    short: 'PROC',
    icon: 'fa-helmet-safety',
    tone: 'warn',
    surface: 'RFIs, daily logs, submittal references',
    summary: 'RFI draft sync active | awaiting one permissions refresh',
    status: 'Needs attention',
    statusMeta: 'Writeback paused on one project',
    scope: 'RFI log + correspondence references',
    writeback: 'Draft RFIs, contradiction notices, assignee handoff notes',
    policy: 'Writes are staged until a human approves',
    owner: 'Project engineer OAuth token',
    nextSync: 'Permission refresh queued for 16:05 IST',
    recent: [
      { time: '15:08', text: 'Draft response for RFI-118 staged for approval.' },
      { time: '14:37', text: 'Daily log pull completed for 3 field questions.' },
      { time: '13:55', text: 'Writeback blocked by missing Admin rights on Pod 4.' },
    ],
  },
  sharepoint: {
    name: 'SharePoint / OneDrive',
    short: 'SP',
    icon: 'fa-cloud',
    tone: 'pass',
    surface: 'Specs, vendor packs, meeting exports',
    summary: '6 libraries watched | revision drift alerts enabled',
    status: 'Healthy',
    statusMeta: 'Folder drift watch active',
    scope: 'Spec libraries + consultant folders',
    writeback: 'Reference links only; source remains in place',
    policy: 'Read-first. No document mutation.',
    owner: 'Entra app registration',
    nextSync: 'Incremental watch every 5 minutes',
    recent: [
      { time: '15:14', text: 'Division 23 folder updated; 3 files queued.' },
      { time: '14:22', text: 'Consultant response PDF linked to contradiction 02.' },
      { time: '13:49', text: 'Duplicate upload prevented by revision hash match.' },
    ],
  },
  revit: {
    name: 'Autodesk Revit',
    short: 'RVT',
    icon: 'fa-cube',
    tone: 'info',
    surface: 'Family parameters and model references',
    summary: 'Model parameter watchlist online for structural + MEP sets',
    status: 'Preview',
    statusMeta: 'Read-only bridge for watched families',
    scope: 'Shared parameters, sheet references, room tags',
    writeback: 'No model writes; reference-only hints',
    policy: 'Preview mode with family-level scoping',
    owner: 'Desktop bridge on coordinator workstation',
    nextSync: 'Manual refresh after each publish',
    recent: [
      { time: '15:02', text: 'Door fire-rating parameters checked against spec clauses.' },
      { time: '14:45', text: 'Shared parameter map refreshed from central model.' },
      { time: '14:11', text: 'Read-only preview generated for MEP family watchlist.' },
    ],
  },
};

const FOCUS_MODES = {
  review: {
    label: 'Risk Review',
    kicker: 'What blocks release right now',
    headline: 'Resolve the contradictions that can still be changed before issue.',
    summary: 'Everything on this screen is tuned for one operator: the VDC lead deciding what changed, what blocks release, and what gets written back.',
    primaryLabel: 'Open review queue',
    primaryRoute: '/demo',
    secondaryLabel: 'Run focused scan',
    secondaryRoute: '/connect',
    dueLabel: 'Owner decisions due today',
    dueValue: '2',
    queue: [
      {
        title: 'Door fire-rating mismatch',
        context: 'A-118 / Door schedule / Division 08',
        impact: 'Inspection delay + rework exposure: $18,000',
        severity: 'critical',
      },
      {
        title: 'Mechanical shaft clearance gap',
        context: 'M-204 / Structural opening / consultant response pending',
        impact: 'Site clash risk before slab pour',
        severity: 'warn',
      },
      {
        title: 'Concrete strength note mismatch',
        context: 'S-302 / spec clause 03 30 00 / ACC issue 241',
        impact: 'Reinforcement hold point at risk',
        severity: 'critical',
      },
    ],
    ledger: [
      { time: '15:16', text: 'Spotter re-scanned 9 linked files after A-221 publish.' },
      { time: '15:05', text: 'Draft contradiction summary staged for owner review.' },
      { time: '14:48', text: 'SharePoint revision drift warning cleared by new upload.' },
      { time: '14:32', text: 'ACC issue 241 linked to latest structural sketch.' },
    ],
    nextActions: [
      'Validate fire-rating source set before owner review.',
      'Approve staged Procore writeback for RFI-118.',
      'Confirm whether shaft opening revision is model-only or issued.',
    ],
    bundle: [
      '3 active contradictions',
      '2 staged writebacks',
      '1 consultant reply missing',
    ],
  },
  release: {
    label: 'Release Prep',
    kicker: 'Get the package out cleanly',
    headline: 'Prepare an issue bundle that can survive procurement and site use.',
    summary: 'The release view compresses connectors, source-of-truth checks, and audit evidence into one place so the package owner can sign off without hunting through tools.',
    primaryLabel: 'Prepare issue bundle',
    primaryRoute: '/connectors',
    secondaryLabel: 'Open connector map',
    secondaryRoute: '/connect',
    dueLabel: 'Release tasks pending',
    dueValue: '4',
    queue: [
      {
        title: 'Sheet A-221 missing latest consultant stamp',
        context: 'ACC publish set vs SharePoint reference folder',
        impact: 'Issue set would carry wrong revision history',
        severity: 'warn',
      },
      {
        title: 'RFI-118 response not attached to release packet',
        context: 'Procore draft ready, package not yet bundled',
        impact: 'Field team sees open question after release',
        severity: 'pending',
      },
      {
        title: 'Room data export not cross-checked against Revit preview',
        context: 'MEP schedule package',
        impact: 'Commissioning handover inconsistency',
        severity: 'warn',
      },
    ],
    ledger: [
      { time: '15:13', text: 'Release bundle IFC-A2 assembled with 17 source references.' },
      { time: '15:01', text: 'Audit snapshot signed for current drawing set.' },
      { time: '14:27', text: 'Field answer pack linked to release notes.' },
      { time: '13:58', text: 'Revision delta between ACC and SharePoint reconciled.' },
    ],
    nextActions: [
      'Confirm every staged writeback has a linked source.',
      'Freeze the issue bundle after final owner approval.',
      'Export the audit snapshot for document control.',
    ],
    bundle: [
      '17 linked source references',
      '4 sign-off checks',
      'Append-only audit snapshot ready',
    ],
  },
  field: {
    label: 'Field Answers',
    kicker: 'Move fast without losing traceability',
    headline: 'Answer the site team quickly, but keep every answer tied to the right source.',
    summary: 'The field view strips the workbench down to the operator loop that matters under pressure: incoming question, best source, draft answer, writeback, and proof.',
    primaryLabel: 'Draft field answer',
    primaryRoute: '/dashboard',
    secondaryLabel: 'Open live demo',
    secondaryRoute: '/demo',
    dueLabel: 'Questions aging > 4h',
    dueValue: '1',
    queue: [
      {
        title: 'Sleeve elevation clarification',
        context: 'Site query from Pod 4 / M-204 / field markup attached',
        impact: 'Concrete team blocked on morning pour',
        severity: 'critical',
      },
      {
        title: 'Door hardware set confirmation',
        context: 'Submittal review tied to Division 08',
        impact: 'Procurement delay if unanswered',
        severity: 'warn',
      },
      {
        title: 'Fire damper access note',
        context: 'Daily log item linked from Procore',
        impact: 'Commissioning walkthrough risk',
        severity: 'pending',
      },
    ],
    ledger: [
      { time: '15:10', text: 'Draft response created for sleeve elevation query.' },
      { time: '14:59', text: 'Field markup attached to linked contradiction set.' },
      { time: '14:18', text: 'Source stack pinned: drawing, spec, consultant email.' },
      { time: '13:44', text: 'Previous field answer promoted to reusable template.' },
    ],
    nextActions: [
      'Send sleeve elevation answer before the pour hold point.',
      'Link the approved response back to Procore and ACC.',
      'Mark reusable answer patterns for future site queries.',
    ],
    bundle: [
      '3 active field questions',
      '1 critical answer due now',
      'Reuse template available',
    ],
  },
};

const COMMANDS = [
  { id: 'focus-review', label: 'Switch focus to Risk Review', kind: 'focus', target: 'review', hint: 'See blockers that still change the release.' },
  { id: 'focus-release', label: 'Switch focus to Release Prep', kind: 'focus', target: 'release', hint: 'Audit the package before issue.' },
  { id: 'focus-field', label: 'Switch focus to Field Answers', kind: 'focus', target: 'field', hint: 'Triage fast-moving site questions.' },
  { id: 'nav-connect', label: 'Open connector onboarding', kind: 'nav', target: '/connect', hint: 'Map a new source without leaving the app.' },
  { id: 'nav-connectors', label: 'Open connector catalog', kind: 'nav', target: '/connectors', hint: 'Review available enterprise integrations.' },
  { id: 'nav-demo', label: 'Open live demo flow', kind: 'nav', target: '/demo', hint: 'Step through the guided inspection workflow.' },
  { id: 'nav-home', label: 'Open landing page', kind: 'nav', target: '/home', hint: 'Return to the narrative product overview.' },
];

let ui = {
  project: PROJECTS[0].id,
  connector: CONNECTOR_ORDER[0],
  focus: 'review',
  paletteOpen: false,
  commandQuery: '',
};

let activeContainer = null;
let keyHandlerAttached = false;

export function renderWorkbench(container) {
  activeContainer = container;
  seedWorkspaceState();

  const project = getProject(ui.project);
  const focus = FOCUS_MODES[ui.focus];
  const connector = CONNECTORS[ui.connector];

  if (typeof document !== 'undefined') {
    document.title = 'Medha Workbench — Connected Document Operations';
  }

  container.innerHTML = `
    <div class="min-h-screen blueprint-bg text-neutral-200 font-sans">
      <header class="border-b border-bp-light/30 bg-bp-dark/80 backdrop-blur-sm sticky top-0 z-50">
        <div class="max-w-[1600px] mx-auto px-4 lg:px-6 py-4 flex flex-wrap items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-sm bg-bp-accent flex items-center justify-center text-white font-bold">M</div>
            <div>
              <h1 class="font-bold text-white">Medha Workbench</h1>
              <p class="text-xs text-neutral-500 font-mono">CONNECTED DOCUMENT OPERATIONS</p>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="badge-info text-[10px]">ONE USER VIEW: VDC LEAD</span>
            <button type="button" class="workbench-toolbar-btn" data-open-palette>
              <i class="fas fa-magnifying-glass text-[11px]"></i>
              <span>COMMANDS</span>
              <span class="text-neutral-600">CMD/CTRL+K</span>
            </button>
            <button type="button" class="workbench-toolbar-btn" data-nav="/connect">
              <i class="fas fa-plug text-[11px]"></i>
              <span>CONNECT SOURCE</span>
            </button>
            <button type="button" class="workbench-toolbar-btn" data-nav="/home">
              <i class="fas fa-compass text-[11px]"></i>
              <span>LANDING</span>
            </button>
          </div>
        </div>
      </header>

      <main class="max-w-[1600px] mx-auto px-4 lg:px-6 py-4 lg:py-5">
        <div class="grid gap-4 xl:grid-cols-12">
          <aside class="xl:col-span-2 space-y-4">
            <section class="workbench-panel">
              <div class="flex items-center justify-between gap-2 mb-3">
                <div>
                  <p class="workbench-kicker">Portfolio</p>
                  <h2 class="text-sm font-semibold text-white">Active projects</h2>
                </div>
                <span class="badge-pass text-[10px]">${PROJECTS.length} LIVE</span>
              </div>
              <div class="space-y-2">
                ${renderProjectRows()}
              </div>
            </section>

            <section class="workbench-panel">
              <p class="workbench-kicker">Today</p>
              <h2 class="text-sm font-semibold text-white mb-3">Operator rhythm</h2>
              <div class="space-y-3 text-sm text-neutral-300">
                <div class="workbench-rail-stat">
                  <span class="text-neutral-500">Current phase</span>
                  <strong class="text-white">${project.phase}</strong>
                </div>
                <div class="workbench-rail-stat">
                  <span class="text-neutral-500">Release object</span>
                  <strong class="text-white">${project.release}</strong>
                </div>
                <div class="workbench-rail-stat">
                  <span class="text-neutral-500">Next decision</span>
                  <strong class="text-white">${project.deadline}</strong>
                </div>
              </div>
            </section>
          </aside>

          <section class="xl:col-span-7 space-y-4">
            <section class="workbench-hero">
              <div class="flex flex-wrap items-start justify-between gap-4">
                <div class="max-w-3xl">
                  <p class="workbench-kicker">${focus.kicker}</p>
                  <h2 class="text-2xl lg:text-3xl font-bold text-white leading-tight">
                    ${project.name}
                  </h2>
                  <p class="text-sm text-neutral-400 mt-2 max-w-2xl leading-relaxed">
                    ${focus.headline}
                  </p>
                  <p class="text-sm text-neutral-500 mt-3 max-w-2xl leading-relaxed">
                    ${focus.summary}
                  </p>
                </div>
                <div class="flex flex-wrap gap-2">
                  <button type="button" class="btn-inspect text-sm font-mono" data-nav="${focus.primaryRoute}">
                    <i class="fas fa-circle-play"></i>${focus.primaryLabel}
                  </button>
                  <button type="button" class="btn-outline text-sm font-mono" data-nav="${focus.secondaryRoute}">
                    <i class="fas fa-arrow-right-arrow-left"></i>${focus.secondaryLabel}
                  </button>
                </div>
              </div>

              <div class="workbench-segmented mt-5" role="tablist" aria-label="Operator focus">
                ${renderFocusButtons()}
              </div>

              <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4 mt-5">
                ${renderHeroMetrics(project, focus)}
              </div>
            </section>

            <section class="grid gap-4 lg:grid-cols-2">
              <div class="workbench-panel">
                <div class="flex items-center justify-between gap-3 mb-3">
                  <div>
                    <p class="workbench-kicker">Connected systems</p>
                    <h3 class="text-sm font-semibold text-white">Existing software, one working view</h3>
                  </div>
                  <span class="badge-info text-[10px]">${project.healthy}/4 HEALTHY</span>
                </div>
                <div class="space-y-2">
                  ${renderConnectorRows()}
                </div>
              </div>

              <div class="workbench-panel">
                <div class="flex items-center justify-between gap-3 mb-3">
                  <div>
                    <p class="workbench-kicker">Selected connector</p>
                    <h3 class="text-sm font-semibold text-white">${connector.name}</h3>
                  </div>
                  <span class="${badgeClass(connector.tone)} text-[10px]">${connector.status.toUpperCase()}</span>
                </div>
                <div class="space-y-3">
                  <div class="workbench-detail-grid">
                    <div>
                      <p class="workbench-label">Reads</p>
                      <p class="text-sm text-neutral-300">${connector.surface}</p>
                    </div>
                    <div>
                      <p class="workbench-label">Writes</p>
                      <p class="text-sm text-neutral-300">${connector.writeback}</p>
                    </div>
                    <div>
                      <p class="workbench-label">Policy</p>
                      <p class="text-sm text-neutral-300">${connector.policy}</p>
                    </div>
                    <div>
                      <p class="workbench-label">Scope owner</p>
                      <p class="text-sm text-neutral-300">${connector.owner}</p>
                    </div>
                  </div>

                  <div class="workbench-inline-note">
                    <i class="fas fa-clock text-bp-accent"></i>
                    <span>${connector.statusMeta}. ${connector.nextSync}.</span>
                  </div>

                  <div>
                    <p class="workbench-label mb-2">Recent connector activity</p>
                    <div class="space-y-1">
                      ${renderConnectorRecent(connector)}
                    </div>
                  </div>
                </div>
              </div>
            </section>

            <section class="workbench-panel">
              <div class="flex items-center justify-between gap-3 mb-3">
                <div>
                  <p class="workbench-kicker">${focus.label}</p>
                  <h3 class="text-sm font-semibold text-white">Decision queue</h3>
                </div>
                <span class="badge-warn text-[10px]">${focus.queue.length} ITEMS</span>
              </div>
              <div class="space-y-2">
                ${renderQueueRows(focus.queue)}
              </div>
            </section>

            <section class="workbench-panel">
              <div class="flex items-center justify-between gap-3 mb-3">
                <div>
                  <p class="workbench-kicker">Change ledger</p>
                  <h3 class="text-sm font-semibold text-white">Everything that changed before you write back</h3>
                </div>
                <span class="badge-info text-[10px]">APPEND ONLY</span>
              </div>
              <div class="space-y-1">
                ${renderLedgerRows(focus.ledger)}
              </div>
            </section>
          </section>

          <aside class="xl:col-span-3 space-y-4">
            <section class="workbench-panel">
              <p class="workbench-kicker">Next best action</p>
              <h3 class="text-sm font-semibold text-white mb-3">${focus.label}</h3>
              <div class="space-y-2">
                ${renderActionRows(focus.nextActions)}
              </div>
            </section>

            <section class="workbench-panel">
              <p class="workbench-kicker">Release bundle</p>
              <h3 class="text-sm font-semibold text-white mb-3">${project.release}</h3>
              <div class="flex flex-wrap gap-2 mb-3">
                ${focus.bundle.map((item) => `<span class="workbench-chip">${item}</span>`).join('')}
              </div>
              <div class="workbench-inline-note">
                <i class="fas fa-shield-halved text-safe-green"></i>
                <span>Coverage ${project.coverage}. All writebacks remain traceable to source documents.</span>
              </div>
            </section>

            <section class="workbench-panel">
              <p class="workbench-kicker">Identity and trust</p>
              <h3 class="text-sm font-semibold text-white mb-3">Human approval stays in the loop</h3>
              <div class="space-y-3 text-sm text-neutral-300">
                <div class="workbench-rail-stat">
                  <span class="text-neutral-500">Current operator</span>
                  <strong class="text-white">You · ${project.owner}</strong>
                </div>
                <div class="workbench-rail-stat">
                  <span class="text-neutral-500">Writeback rule</span>
                  <strong class="text-white">Nothing destructive. Notes and staged drafts only.</strong>
                </div>
                <div class="workbench-rail-stat">
                  <span class="text-neutral-500">Audit position</span>
                  <strong class="text-white">Every answer carries the source stack and revision trail.</strong>
                </div>
              </div>
            </section>
          </aside>
        </div>
      </main>

      ${renderCommandPalette()}
    </div>
  `;

  wireWorkbenchEvents();
  attachKeyHandler();
  syncCommandPalette();
}

function renderProjectRows() {
  return PROJECTS.map((project) => {
    const active = project.id === ui.project ? 'workbench-item workbench-item-active' : 'workbench-item';
    return `
      <button type="button" class="${active}" data-project="${project.id}">
        <div class="flex items-center justify-between gap-2">
          <div class="text-left">
            <div class="text-sm font-semibold text-white">${project.name}</div>
            <div class="text-[11px] text-neutral-500 font-mono">${project.client.toUpperCase()}</div>
          </div>
          <span class="${project.blockers > 1 ? 'badge-critical' : 'badge-warn'} text-[10px]">${project.blockers}</span>
        </div>
        <div class="workbench-item-meta mt-2">
          <span>${project.docs} DOCS</span>
          <span>${project.healthy}/4 LINKS</span>
          <span>${project.coverage} COVERAGE</span>
        </div>
      </button>
    `;
  }).join('');
}

function renderFocusButtons() {
  return Object.entries(FOCUS_MODES).map(([key, focus]) => {
    const active = key === ui.focus ? 'workbench-segment workbench-segment-active' : 'workbench-segment';
    return `
      <button type="button" class="${active}" data-focus="${key}">
        <span>${focus.label}</span>
      </button>
    `;
  }).join('');
}

function renderHeroMetrics(project, focus) {
  const metrics = [
    {
      value: project.docs,
      label: 'Documents in live scope',
      detail: `${formatNumber(project.chunks)} indexed chunks`,
    },
    {
      value: `${project.healthy}/4`,
      label: 'Connectors healthy',
      detail: `${project.writebacks} staged writebacks`,
    },
    {
      value: project.blockers,
      label: 'Open blockers',
      detail: project.deadline,
    },
    {
      value: focus.dueValue,
      label: focus.dueLabel,
      detail: project.release,
    },
  ];

  return metrics.map((metric) => `
    <div class="workbench-metric">
      <div class="text-2xl font-bold text-white">${metric.value}</div>
      <div class="text-xs font-mono text-neutral-500 mt-1">${metric.label.toUpperCase()}</div>
      <div class="text-sm text-neutral-300 mt-3">${metric.detail}</div>
    </div>
  `).join('');
}

function renderConnectorRows() {
  return CONNECTOR_ORDER.map((key) => {
    const connector = CONNECTORS[key];
    const active = key === ui.connector ? 'workbench-item workbench-item-active' : 'workbench-item';
    return `
      <button type="button" class="${active}" data-connector="${key}">
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-start gap-3 text-left">
            <div class="w-9 h-9 rounded-sm bg-bp-dark/80 border border-bp-light/30 flex items-center justify-center text-bp-accent">
              <i class="fas ${connector.icon} text-sm"></i>
            </div>
            <div>
              <div class="text-sm font-semibold text-white">${connector.name}</div>
              <div class="text-[11px] text-neutral-500 font-mono">${connector.surface.toUpperCase()}</div>
            </div>
          </div>
          <span class="${badgeClass(connector.tone)} text-[10px]">${connector.short}</span>
        </div>
        <div class="text-sm text-neutral-300 mt-3 text-left">${connector.summary}</div>
      </button>
    `;
  }).join('');
}

function renderConnectorRecent(connector) {
  return connector.recent.map((item) => `
    <div class="workbench-ledger-row">
      <span class="workbench-ledger-time">${item.time}</span>
      <span class="text-sm text-neutral-300">${item.text}</span>
    </div>
  `).join('');
}

function renderQueueRows(queue) {
  return queue.map((item) => `
    <div class="workbench-row workbench-row-${item.severity}">
      <div class="flex items-start justify-between gap-3">
        <div>
          <div class="text-sm font-semibold text-white">${item.title}</div>
          <div class="text-xs font-mono text-neutral-500 mt-1">${item.context.toUpperCase()}</div>
        </div>
        <span class="${badgeClass(item.severity)} text-[10px]">${item.severity.toUpperCase()}</span>
      </div>
      <div class="text-sm text-neutral-300 mt-3">${item.impact}</div>
    </div>
  `).join('');
}

function renderLedgerRows(ledger) {
  return ledger.map((item) => `
    <div class="workbench-ledger-row">
      <span class="workbench-ledger-time">${item.time}</span>
      <span class="text-sm text-neutral-300">${item.text}</span>
    </div>
  `).join('');
}

function renderActionRows(actions) {
  return actions.map((action, index) => `
    <div class="workbench-row">
      <div class="flex items-start gap-3">
        <span class="workbench-step">${index + 1}</span>
        <span class="text-sm text-neutral-300">${action}</span>
      </div>
    </div>
  `).join('');
}

function renderCommandPalette() {
  const hidden = ui.paletteOpen ? '' : ' hidden';

  return `
    <div id="workbench-command-backdrop" class="workbench-command-backdrop${hidden}" data-close-palette>
      <div class="workbench-command" role="dialog" aria-modal="true" aria-label="Command palette">
        <div class="flex items-center gap-3 border-b border-bp-light/30 px-4 py-3">
          <i class="fas fa-magnifying-glass text-neutral-500 text-sm"></i>
          <input
            id="workbench-command-input"
            class="workbench-command-input"
            type="text"
            value="${escapeAttr(ui.commandQuery)}"
            placeholder="Switch focus, open flows, jump to a route"
            autocomplete="off"
          >
          <button type="button" class="text-xs text-neutral-500 hover:text-white transition font-mono" data-close-palette>
            ESC
          </button>
        </div>
        <div id="workbench-command-results" class="p-2 max-h-[360px] overflow-y-auto">
          ${renderCommandResults()}
        </div>
      </div>
    </div>
  `;
}

function renderCommandResults() {
  const query = ui.commandQuery.trim().toLowerCase();
  const filtered = COMMANDS.filter((command) => {
    if (!query) return true;
    return `${command.label} ${command.hint}`.toLowerCase().includes(query);
  });

  if (!filtered.length) {
    return `
      <div class="px-3 py-6 text-sm text-neutral-500 font-mono">
        No commands match "${escapeHtml(ui.commandQuery)}".
      </div>
    `;
  }

  return filtered.map((command) => `
    <button type="button" class="workbench-command-item" data-command="${command.id}">
      <span class="text-sm font-semibold text-white">${command.label}</span>
      <span class="text-xs text-neutral-500 mt-1">${command.hint}</span>
    </button>
  `).join('');
}

function wireWorkbenchEvents() {
  if (!activeContainer) return;

  activeContainer.querySelectorAll('[data-nav]').forEach((element) => {
    element.addEventListener('click', () => navigate(element.dataset.nav));
  });

  activeContainer.querySelectorAll('[data-project]').forEach((element) => {
    element.addEventListener('click', () => {
      ui.project = element.dataset.project;
      state.currentProject = ui.project;
      renderWorkbench(activeContainer);
    });
  });

  activeContainer.querySelectorAll('[data-connector]').forEach((element) => {
    element.addEventListener('click', () => {
      ui.connector = element.dataset.connector;
      renderWorkbench(activeContainer);
    });
  });

  activeContainer.querySelectorAll('[data-focus]').forEach((element) => {
    element.addEventListener('click', () => {
      ui.focus = element.dataset.focus;
      renderWorkbench(activeContainer);
    });
  });

  activeContainer.querySelectorAll('[data-open-palette]').forEach((element) => {
    element.addEventListener('click', () => {
      ui.paletteOpen = true;
      renderWorkbench(activeContainer);
    });
  });

  const backdrop = activeContainer.querySelector('#workbench-command-backdrop');
  backdrop?.addEventListener('click', (event) => {
    if (event.target instanceof HTMLElement && event.target.dataset.closePalette !== undefined) {
      closePalette();
    }
  });

}

function syncCommandPalette() {
  const input = document.getElementById('workbench-command-input');
  const results = document.getElementById('workbench-command-results');
  if (!input || !results) return;

  input.addEventListener('input', (event) => {
    ui.commandQuery = event.target.value;
    results.innerHTML = renderCommandResults();
    results.querySelectorAll('[data-command]').forEach((element) => {
      element.addEventListener('click', () => executeCommand(element.dataset.command));
    });
  });

  window.setTimeout(() => input.focus(), 0);
}

function executeCommand(id) {
  const command = COMMANDS.find((item) => item.id === id);
  if (!command) return;

  if (command.kind === 'focus') {
    ui.focus = command.target;
    closePalette();
    renderWorkbench(activeContainer);
    return;
  }

  closePalette();
  navigate(command.target);
}

function closePalette() {
  ui.paletteOpen = false;
  ui.commandQuery = '';
  if (activeContainer) renderWorkbench(activeContainer);
}

function attachKeyHandler() {
  if (keyHandlerAttached || typeof document === 'undefined') return;

  document.addEventListener('keydown', (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
      event.preventDefault();
      ui.paletteOpen = true;
      if (activeContainer) renderWorkbench(activeContainer);
      return;
    }

    if (event.key === 'Escape' && ui.paletteOpen) {
      event.preventDefault();
      closePalette();
    }
  });

  keyHandlerAttached = true;
}

function seedWorkspaceState() {
  if (!state.projects.length) {
    state.projects = PROJECTS.map((project) => ({
      id: project.id,
      name: project.name,
      document_count: project.docs,
      chunk_count: project.chunks,
    }));
  }

  if (!getProject(state.currentProject)) {
    state.currentProject = PROJECTS[0].id;
  }

  if (!getProject(ui.project)) {
    ui.project = state.currentProject || PROJECTS[0].id;
  }
}

function getProject(id) {
  return PROJECTS.find((project) => project.id === id);
}

function badgeClass(tone) {
  switch (tone) {
    case 'pass':
      return 'badge-pass';
    case 'warn':
      return 'badge-warn';
    case 'critical':
      return 'badge-critical';
    case 'pending':
      return 'badge-pending';
    default:
      return 'badge-info';
  }
}

function formatNumber(value) {
  return new Intl.NumberFormat('en-US').format(value);
}

function escapeAttr(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}
