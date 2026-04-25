/**
 * info-boxes.js — Outreach Page Supplementary Info Boxes
 * SRP: Renders JTBD reminder and methodology explanation.
 */

export function renderJTBDBox() {
  const jobs = [
    ['01', '"Find the spec clause before the concrete truck arrives" — Retrieve facts in <10 seconds'],
    ['02', '"Catch contradictions before they cost $50K in rework" — Auto-scan specs vs. drawings'],
    ['03', '"Draft RFIs that architects actually answer quickly" — Auto-reference source documents'],
    ['04', '"Onboard new engineers without losing tribal knowledge" — Searchable project memory'],
    ['05', '"Prove to the owner we checked everything" — Generate audit trails + evidence'],
  ];
  const cells = jobs.map(([n, text]) => `
    <div class="flex items-start gap-2 ${n === '05' ? 'md:col-span-2' : ''}">
      <span class="text-bp-accent font-mono font-bold">${n}</span>
      <span>${text}</span>
    </div>
  `).join('');

  return `
    <div class="mt-8 card-structural border-bp-accent/30 bg-bp-accent/5">
      <h3 class="text-sm font-bold text-white mb-3 font-mono">THE 5 JOBS MEDHA IS HIRED FOR</h3>
      <div class="grid md:grid-cols-2 gap-4 text-xs text-gray-400">${cells}</div>
    </div>
  `;
}

export function renderMethodologyBox() {
  return `
    <div class="mt-6 card-structural border-bp-light/30">
      <h3 class="text-sm font-bold text-white mb-3 font-mono">RESEARCH METHODOLOGY</h3>
      <div class="grid md:grid-cols-2 gap-4 text-xs text-gray-400">
        <div>
          <p class="text-white font-semibold mb-1">How Targets Were Selected</p>
          <p class="leading-relaxed">
            1. Job posting analysis (VDC/BM hiring = active pain)<br>
            2. Conference speaker lists (thought leaders = receptive)<br>
            3. Case study research (digital maturity = ready)<br>
            4. Government mandate mapping (compliance = urgency)
          </p>
        </div>
        <div>
          <p class="text-white font-semibold mb-1">How Messages Were Crafted</p>
          <p class="leading-relaxed">
            1. JTBD-aligned: asks about THEIR job<br>
            2. Specific context: references projects, roles<br>
            3. Social proof: "Most teams say..."<br>
            4. Low-friction CTA: "10-min conversation"<br>
            5. Outcome-framed: time saved, risk reduced
          </p>
        </div>
      </div>
      <div class="mt-4 pt-3 border-t border-bp-light/20">
        <p class="text-white font-semibold mb-1">LinkedIn Profile URL Research</p>
        <p class="leading-relaxed">
          Exact <code class="text-bp-accent font-mono">linkedin.com/in/...</code> profile URLs are NOT publicly discoverable via web search — LinkedIn blocks indexing via robots.txt and login walls. Discovery strategy: (1) Conference speaker pages → name + role + company, (2) Publication author bios → affiliations, (3) Webinar registrations → contact titles, (4) LinkedIn people search as fallback. All "Find on LinkedIn" buttons route to LinkedIn\'s own search results for the contact + company combination.
        </p>
      </div>
      <p class="text-[10px] text-gray-600 mt-3 font-mono">
        [CITE: Gracker2025] Gracker.ai analysis (20M+ outreach attempts). Personalized outreach outperforms templated by 3x. https://gracker.ai/blog/increase-linkedin-acceptance-rate
        [CITE: Cialdini1984] Social proof referencing similar firms increases response rates.
      </p>
    </div>
  `;
}
