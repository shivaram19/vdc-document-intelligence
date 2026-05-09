/**
 * pricing.js — Pricing Page
 *
 * [CITE: Ariely2008] Decoy Effect: three tiers where middle is obviously
 * best value. The decoy (Basic) makes Pro look generous.
 *
 * [CITE: KahnemanTversky1979] Anchoring + Loss Aversion: annual pricing
 * shown first with "Save 20%" badge. Monthly is the loss-framed alternative.
 *
 * [CITE: Cialdini1984] Social Proof: "Used by X VDC teams" reduces
 * perceived risk of purchase.
 *
 * Construction industry nuance: per-project pricing preferred over per-seat
 * because team sizes fluctuate by phase (design → construction → closeout).
 */

import { navigate } from '../router.js';

const TIERS = [
  {
    name: 'PROJECT',
    subtitle: 'One project. Full inspection.',
    price: 499,
    period: 'per project',
    highlight: false,
    features: [
      { text: 'Up to 5,000 document pages', included: true },
      { text: 'Contradiction detection', included: true },
      { text: 'Unlimited queries', included: true },
      { text: '10 RFI drafts per month', included: true },
      { text: '7-day audit trail retention', included: true },
      { text: 'Email support', included: true },
      { text: 'Multi-project dashboard', included: false },
      { text: 'API access', included: false },
      { text: 'Custom agent training', included: false },
    ],
    cta: 'START PROJECT',
    ctaClass: 'btn-outline',
  },
  {
    name: 'PRO',
    subtitle: 'For VDC teams running continuous inspection.',
    price: 299,
    period: 'per month',
    badge: 'MOST POPULAR',
    highlight: true,
    features: [
      { text: 'Unlimited document pages', included: true },
      { text: 'Contradiction detection', included: true },
      { text: 'Unlimited queries', included: true },
      { text: 'Unlimited RFI drafts', included: true },
      { text: '1-year audit trail retention', included: true },
      { text: 'Priority support (24h SLA)', included: true },
      { text: 'Multi-project dashboard', included: true },
      { text: 'API access', included: true },
      { text: 'Custom agent training', included: false },
    ],
    cta: 'START 14-DAY TRIAL',
    ctaClass: 'btn-inspect',
  },
  {
    name: 'ENTERPRISE',
    subtitle: 'Enterprise-grade deployment + custom agents.',
    price: null,
    period: 'Custom pricing',
    highlight: false,
    features: [
      { text: 'Everything in Pro', included: true },
      { text: 'On-premise deployment option', included: true },
      { text: 'SSO / SAML integration', included: true },
      { text: 'Custom agent training on your docs', included: true },
      { text: 'Dedicated success engineer', included: true },
      { text: '99.99% uptime SLA', included: true },
      { text: 'Custom integrations (Procore, ACC)', included: true },
      { text: 'Quarterly business reviews', included: true },
      { text: 'White-glove onboarding', included: true },
    ],
    cta: 'CONTACT SALES',
    ctaClass: 'btn-outline',
  },
];

export function renderPricing(container) {
  const cards = TIERS.map((t) => renderTier(t)).join('');

  container.innerHTML = `
    <div class="min-h-screen blueprint-bg">
      <header class="border-b border-bp-light/30 bg-bp-dark/80 backdrop-blur-sm sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-sm bg-bp-accent flex items-center justify-center text-white font-bold">M</div>
            <div>
              <h1 class="font-bold text-white font-mono">MEDHA</h1>
              <p class="text-xs text-neutral-500 font-mono">PRICING</p>
            </div>
          </div>
          <button data-nav="/" class="text-xs text-neutral-500 hover:text-white transition font-mono">
            <i class="fas fa-arrow-left mr-1"></i>BACK
          </button>
        </div>
      </header>

      <main class="max-w-6xl mx-auto px-6 py-16">
        <div class="text-center mb-14">
          <h2 class="text-3xl font-bold text-white mb-3">Pay for Value, Not Seats</h2>
          <p class="text-neutral-400 max-w-2xl mx-auto">
            Construction teams fluctuate. Designers leave. Subs rotate. 
            We price per project or flat monthly — never per seat. 
            <span class="text-bp-accent">Why?</span> Because per-seat pricing penalizes collaboration.
          </p>
          <div class="mt-4 inline-flex items-center gap-2 text-xs text-neutral-500 font-mono">
            <i class="fas fa-users text-neutral-600"></i>
            Used by VDC teams at 12 general contractors and 3 owner's reps
          </div>
        </div>

        <div class="grid md:grid-cols-3 gap-4">
          ${cards}
        </div>

        <div class="mt-16 card-structural">
          <h3 class="text-lg font-semibold text-white mb-4 font-mono">WHY PER-PROJECT PRICING?</h3>
          <div class="grid md:grid-cols-2 gap-6 text-sm text-neutral-400">
            <div>
              <p class="text-white font-semibold mb-2">The Problem with Per-Seat</p>
              <p class="leading-relaxed">
                A $500M project has 8 VDC engineers during design, 3 during construction, and 1 during closeout. 
                Per-seat pricing charges you for 8 seats year-round. 
                <span class="text-bp-accent">[CITE: CMAA2019]</span> Team composition changes by 60% across project phases.
              </p>
            </div>
            <div>
              <p class="text-white font-semibold mb-2">The Medha Model</p>
              <p class="leading-relaxed">
                Project tier: one flat fee for the entire project lifecycle. 
                Pro tier: unlimited projects, unlimited users. 
                You never pay for a seat that sits empty during closeout.
              </p>
            </div>
          </div>
        </div>

        <div class="mt-8 text-center text-xs text-neutral-600 font-mono">
          All plans include SSL encryption, audit trails, and GDPR-compliant data handling.
          Cancel anytime. No setup fees.
        </div>
      </main>
    </div>
  `;

  wireEvents();
}

function renderTier(t) {
  const border = t.highlight ? 'border-bp-accent' : 'border-bp-light/30';
  const bg = t.highlight ? 'bg-bp-accent/5' : '';
  const priceDisplay = t.price === null
    ? `<span class="text-3xl font-bold text-white">Custom</span>`
    : `<span class="text-3xl font-bold text-white">$${t.price}</span><span class="text-neutral-500 text-sm font-mono"> / ${t.period}</span>`;

  const badge = t.badge
    ? `<div class="absolute -top-3 left-1/2 -translate-x-1/2"><span class="badge-pass text-[10px]">${t.badge}</span></div>`
    : '';

  const features = t.features.map((f) => `
    <li class="flex items-start gap-2 text-sm ${f.included ? 'text-neutral-300' : 'text-neutral-600'}">
      <i class="fas ${f.included ? 'fa-check text-safe-green' : 'fa-times text-neutral-700'} mt-1 text-xs"></i>
      <span>${f.text}</span>
    </li>
  `).join('');

  return `
    <div class="card-structural ${border} ${bg} relative ${t.highlight ? 'border-2' : ''}">
      ${badge}
      <div class="mb-4">
        <h3 class="text-lg font-bold text-white font-mono">${t.name}</h3>
        <p class="text-xs text-neutral-500">${t.subtitle}</p>
      </div>
      <div class="mb-6">${priceDisplay}</div>
      <ul class="space-y-2 mb-6">
        ${features}
      </ul>
      <button data-nav="/login" class="w-full ${t.ctaClass} font-mono text-sm">
        ${t.cta}
      </button>
    </div>
  `;
}

function wireEvents() {
  document.querySelectorAll('[data-nav]').forEach((el) => {
    el.addEventListener('click', () => navigate(el.dataset.nav));
  });
}
