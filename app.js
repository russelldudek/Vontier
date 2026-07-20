const scenarios = {
  uptime: {
    title: 'Field uptime signal',
    status: 'Coupling',
    description: 'Combine machine telemetry, support tickets, parts history, and technician judgment before automating a maintenance recommendation.',
    gates: [
      ['Evidence', 'Working', 'Telemetry and issue history are available; failure labels need normalization.'],
      ['Authority', 'Explicit', 'Technician retains release authority for high-consequence action.'],
      ['Ownership', 'Ready', 'Product, service, and operations share one outcome review.']
    ],
    output: 'Controlled pilot -> production evidence pack'
  },
  payments: {
    title: 'Payment reliability signal',
    status: 'Open',
    description: 'Use transaction, device, site, and support signals to isolate failure patterns while preserving payment-security and customer-impact controls.',
    gates: [
      ['Evidence', 'Working', 'Failure paths are observable; cross-platform taxonomy is incomplete.'],
      ['Authority', 'Bounded', 'Security and payments owners define non-negotiable release controls.'],
      ['Ownership', 'Forming', 'One accountable value-stream owner must be named before scale.']
    ],
    output: 'Discovery sprint -> reusable fault taxonomy'
  },
  productivity: {
    title: 'Multi-site productivity signal',
    status: 'Lock-up',
    description: 'Standardize a proven workflow pattern across business units while preserving local operating constraints and explicit exception paths.',
    gates: [
      ['Evidence', 'Ready', 'Baseline, intervention, and adoption behavior are measurable.'],
      ['Authority', 'Explicit', 'Local operators retain exception and escalation authority.'],
      ['Ownership', 'Ready', 'Enterprise platform and business-unit owners share the release contract.']
    ],
    output: 'Reusable architecture -> scaled deployment'
  },
  energy: {
    title: 'Energy optimization signal',
    status: 'Coupling',
    description: 'Balance charging schedules, energy cost, asset availability, and fleet commitments through a governed recommendation workflow.',
    gates: [
      ['Evidence', 'Working', 'Demand, tariff, utilization, and asset-state signals are available.'],
      ['Authority', 'Explicit', 'Fleet operations owns service commitments and override policy.'],
      ['Ownership', 'Ready', 'Product and customer teams agree on value and trust measures.']
    ],
    output: 'Customer co-innovation -> instrumented pilot'
  }
};

const tabs = [...document.querySelectorAll('[data-scenario]')];
const title = document.querySelector('[data-sim-title]');
const desc = document.querySelector('[data-sim-description]');
const status = document.querySelector('[data-sim-status]');
const gates = [...document.querySelectorAll('[data-gate]')];
const output = document.querySelector('[data-output]');

function setScenario(key) {
  const s = scenarios[key];
  if (!s || !title) return;
  tabs.forEach(btn => btn.setAttribute('aria-selected', String(btn.dataset.scenario === key)));
  title.textContent = s.title;
  desc.textContent = s.description;
  status.textContent = s.status;
  gates.forEach((gate, i) => {
    gate.querySelector('span').textContent = s.gates[i][0];
    gate.querySelector('strong').textContent = s.gates[i][1];
    gate.querySelector('small').textContent = s.gates[i][2];
  });
  output.textContent = s.output;
  document.documentElement.dataset.mode = s.status.toLowerCase().replace(/\s+/g,'-');
}

tabs.forEach(btn => btn.addEventListener('click', () => setScenario(btn.dataset.scenario)));
tabs.forEach((btn, index) => btn.addEventListener('keydown', event => {
  if (!['ArrowDown','ArrowUp','ArrowLeft','ArrowRight'].includes(event.key)) return;
  event.preventDefault();
  const direction = ['ArrowDown','ArrowRight'].includes(event.key) ? 1 : -1;
  const next = tabs[(index + direction + tabs.length) % tabs.length];
  next.focus();
  setScenario(next.dataset.scenario);
}));
setScenario('uptime');
