'use client';

import React, { useState } from 'react';

const API = (process.env.NEXT_PUBLIC_API_URL ?? 'https://afyarisk-engine-production.up.railway.app') + '/api/v1';

// ─── Design tokens (light professional theme) ─────────────────────────────────
// Surface:  #ffffff cards on #f8f7f4 background
// Border:   #e2e0db
// Brand:    #0d6e4e (forest green)
// Text:     #1a1a1a primary · #6b6860 muted · #9c9890 placeholder
// Status:   emerald=good · amber=warn · red=bad

// ─── Shared helpers ────────────────────────────────────────────────────────────

function Badge({ label, color }: { label: string; color: string }) {
  const map: Record<string, string> = {
    green:  'bg-emerald-50 text-emerald-700 border-emerald-200',
    yellow: 'bg-amber-50 text-amber-700 border-amber-200',
    red:    'bg-red-50 text-red-700 border-red-200',
    blue:   'bg-sky-50 text-sky-700 border-sky-200',
  };
  return (
    <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${map[color] ?? map.blue}`}>
      {label}
    </span>
  );
}

function Card({ title, value, sub, color = 'brand' }: { title: string; value: string; sub?: string; color?: string }) {
  const cv: Record<string, string> = {
    brand:   'text-[#0d6e4e]',
    emerald: 'text-emerald-600',
    amber:   'text-amber-600',
    blue:    'text-sky-600',
    red:     'text-red-600',
    muted:   'text-[#1a1a1a]',
    violet:  'text-violet-600',
  };
  return (
    <div className="bg-white border border-[#e2e0db] rounded-lg p-4">
      <span className="text-xs text-[#6b6860] block mb-1 font-medium uppercase tracking-wide">{title}</span>
      <span className={`text-xl font-bold ${cv[color] ?? cv.brand}`}>{value}</span>
      {sub && <span className="text-xs text-[#9c9890] block mt-0.5">{sub}</span>}
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white border border-[#e2e0db] rounded-xl p-6 shadow-sm">
      <h2 className="text-sm font-semibold text-[#1a1a1a] mb-5 pb-3 border-b border-[#e2e0db]">{title}</h2>
      {children}
    </div>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return <label className="block text-xs font-medium text-[#6b6860] mb-1">{children}</label>;
}

const inputCls = 'w-full bg-[#faf9f7] border border-[#e2e0db] rounded-lg px-3 py-2 text-sm text-[#1a1a1a] focus:outline-none focus:border-[#0d6e4e] focus:ring-1 focus:ring-[#0d6e4e]/20 transition-colors';

function Btn({ children, disabled, color = 'brand' }: { children: React.ReactNode; disabled?: boolean; color?: string }) {
  const cv: Record<string, string> = {
    brand:  'bg-[#0d6e4e] hover:bg-[#0a5c40] text-white',
    red:    'bg-red-600 hover:bg-red-700 text-white',
    violet: 'bg-violet-600 hover:bg-violet-700 text-white',
    green:  'bg-emerald-600 hover:bg-emerald-700 text-white',
  };
  return (
    <button type="submit" disabled={disabled}
      className={`w-full ${cv[color] ?? cv.brand} disabled:opacity-40 font-medium py-2.5 rounded-lg text-sm mt-2 transition-colors`}>
      {children}
    </button>
  );
}

function ErrorBox({ msg }: { msg: string }) {
  return (
    <div className="mt-4 bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-xs font-mono">
      {msg}
    </div>
  );
}

function Spinner() {
  return <span className="inline-block w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin mr-2 align-middle" />;
}

function Empty({ text }: { text: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-48 gap-2">
      <div className="w-8 h-8 rounded-full bg-[#f0ede8] flex items-center justify-center">
        <span className="text-[#9c9890] text-sm">—</span>
      </div>
      <p className="text-xs text-[#9c9890] text-center max-w-xs">{text}</p>
    </div>
  );
}

// ─── Tab 1: Health Risk Assessment ────────────────────────────────────────────

function HealthTab() {
  const [form, setForm] = useState({ glucose: 120, bmi: 27.5, age: 42, blood_pressure: 80, insulin: 85 });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setLoading(true); setError('');
    try {
      const res = await fetch(`${API}/assess-health-risk`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) { const d = await res.json(); throw new Error(d.detail ?? res.statusText); }
      setResult(await res.json());
    } catch (err: any) { setError(err.message); }
    finally { setLoading(false); }
  };

  const tierColor = (t: string) => ({ Low: 'green', Medium: 'yellow', High: 'red' }[t] ?? 'blue');

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Panel title="Patient Biomarkers">
        <form onSubmit={submit} className="space-y-3">
          {[
            { key: 'glucose',        label: 'Blood Glucose (mg/dL)',    min: 60,  max: 300, step: 1   },
            { key: 'bmi',            label: 'BMI (kg/m²)',              min: 10,  max: 60,  step: 0.1 },
            { key: 'age',            label: 'Age (years)',              min: 18,  max: 100, step: 1   },
            { key: 'blood_pressure', label: 'Blood Pressure (mmHg)',    min: 40,  max: 200, step: 1   },
            { key: 'insulin',        label: 'Insulin (μU/mL)',          min: 0,   max: 900, step: 1   },
          ].map(({ key, label, min, max, step }) => (
            <div key={key}>
              <Label>{label}</Label>
              <input type="number" min={min} max={max} step={step}
                value={(form as any)[key]}
                onChange={e => setForm({ ...form, [key]: Number(e.target.value) })}
                className={inputCls} />
            </div>
          ))}
          <Btn disabled={loading}>{loading ? <><Spinner />Assessing...</> : 'Run Health Assessment'}</Btn>
        </form>
        {error && <ErrorBox msg={error} />}
      </Panel>

      <Panel title="Assessment Results">
        {result ? (
          <div className="space-y-5">
            <div className="flex items-center gap-3">
              <span className="text-xs font-medium text-[#6b6860]">Risk Tier</span>
              <Badge label={result.risk_tier} color={tierColor(result.risk_tier)} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Card title="Risk Score"               value={(result.risk_score * 100).toFixed(1) + '%'}           color="amber"   />
              <Card title="Confidence"               value={(result.confidence * 100).toFixed(1) + '%'}            color="blue"    />
              <Card title="Survival Prob. (3yr)"     value={(result.survival_probability * 100).toFixed(1) + '%'}  color="emerald" />
              <Card title="Health Degradation (3yr)" value={(result.health_degradation_3yr * 100).toFixed(1) + '%'} color="red"    />
            </div>
            <div className="border-t border-[#e2e0db] pt-4">
              <p className="text-xs font-semibold text-[#6b6860] uppercase tracking-wide mb-3">Actuarial Premium</p>
              <div className="grid grid-cols-2 gap-3">
                <Card title="Annual Premium"  value={`KES ${result.annual_premium.toLocaleString()}`}  color="brand" />
                <Card title="Monthly Premium" value={`KES ${result.monthly_premium.toLocaleString()}`} color="muted" />
                <Card title="Pure Premium"    value={`KES ${result.pure_premium.toLocaleString()}`}    color="muted" />
                <Card title="Risk Multiplier" value={`${result.risk_multiplier.toFixed(2)}×`}          color="amber" />
              </div>
            </div>
          </div>
        ) : (
          <Empty text="Submit patient biomarkers to see clinical risk assessment and actuarial premium." />
        )}
      </Panel>
    </div>
  );
}

// ─── Tab 2: Policy Pricing ─────────────────────────────────────────────────────

function PricingTab() {
  const [form, setForm] = useState({ risk_tier: 'Medium', risk_score: 0.5, base_frequency: '', base_severity: '', target_loss_ratio: '', expense_loading: '' });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setLoading(true); setError('');
    const payload: any = { risk_tier: form.risk_tier, risk_score: Number(form.risk_score) };
    if (form.base_frequency)    payload.base_frequency    = Number(form.base_frequency);
    if (form.base_severity)     payload.base_severity     = Number(form.base_severity);
    if (form.target_loss_ratio) payload.target_loss_ratio = Number(form.target_loss_ratio);
    if (form.expense_loading)   payload.expense_loading   = Number(form.expense_loading);
    try {
      const res = await fetch(`${API}/price-policy`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
      });
      if (!res.ok) { const d = await res.json(); throw new Error(d.detail ?? res.statusText); }
      setResult(await res.json());
    } catch (err: any) { setError(err.message); }
    finally { setLoading(false); }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Panel title="Pricing Parameters">
        <form onSubmit={submit} className="space-y-3">
          <div>
            <Label>Risk Tier</Label>
            <select value={form.risk_tier} onChange={e => setForm({ ...form, risk_tier: e.target.value })} className={inputCls}>
              <option>Low</option><option>Medium</option><option>High</option>
            </select>
          </div>
          <div>
            <Label>Risk Score (0.0 – 1.0)</Label>
            <input type="number" min={0} max={1} step={0.01} value={form.risk_score}
              onChange={e => setForm({ ...form, risk_score: Number(e.target.value) })} className={inputCls} />
          </div>
          <p className="text-xs text-[#9c9890] pt-1 font-medium uppercase tracking-wide">Optional overrides</p>
          {[
            { key: 'base_frequency',    label: 'Base Claim Frequency (per year)', placeholder: 'default: 0.15'    },
            { key: 'base_severity',     label: 'Base Severity (KES)',             placeholder: 'default: 50,000'  },
            { key: 'target_loss_ratio', label: 'Target Loss Ratio',               placeholder: 'default: 0.65'    },
            { key: 'expense_loading',   label: 'Expense Loading Factor',          placeholder: 'default: 0.15'    },
          ].map(({ key, label, placeholder }) => (
            <div key={key}>
              <Label>{label}</Label>
              <input type="number" step="any" placeholder={placeholder}
                value={(form as any)[key]}
                onChange={e => setForm({ ...form, [key]: e.target.value })}
                className={inputCls + ' placeholder:text-[#c0bdb8]'} />
            </div>
          ))}
          <Btn disabled={loading}>{loading ? <><Spinner />Calculating...</> : 'Calculate Premium'}</Btn>
        </form>
        {error && <ErrorBox msg={error} />}
      </Panel>

      <Panel title="Premium Breakdown">
        {result ? (
          <div className="space-y-5">
            <div className="grid grid-cols-2 gap-3">
              <Card title="Annual Premium"  value={`KES ${result.annual_premium.toLocaleString()}`}  color="brand"  />
              <Card title="Monthly Premium" value={`KES ${result.monthly_premium.toLocaleString()}`} color="blue"   />
              <Card title="Pure Premium"    value={`KES ${result.pure_premium.toLocaleString()}`}    color="muted"  />
              <Card title="Risk Multiplier" value={`${result.risk_multiplier.toFixed(2)}×`}          color="amber"  />
            </div>
            <div className="border-t border-[#e2e0db] pt-4">
              <p className="text-xs font-semibold text-[#6b6860] uppercase tracking-wide mb-3">Loading Factors</p>
              <div className="space-y-2 text-xs font-mono">
                {Object.entries(result.loading_factors).map(([k, v]) => (
                  <div key={k} className="flex justify-between py-1 border-b border-[#f0ede8]">
                    <span className="text-[#6b6860]">{k}</span>
                    <span className="font-semibold text-[#1a1a1a]">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="border-t border-[#e2e0db] pt-4">
              <p className="text-xs font-semibold text-[#6b6860] uppercase tracking-wide mb-3">Actuarial Breakdown</p>
              <div className="space-y-2 text-xs font-mono">
                {Object.entries(result.breakdown).map(([k, v]) => (
                  <div key={k} className="flex justify-between py-1 border-b border-[#f0ede8]">
                    <span className="text-[#6b6860]">{k}</span>
                    <span className="font-semibold text-[#1a1a1a]">{String(v)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <Empty text="Set risk parameters and calculate to see the full premium breakdown." />
        )}
      </Panel>
    </div>
  );
}

// ─── Tab 3: Fraud Detection ────────────────────────────────────────────────────

function FraudTab() {
  const [form, setForm] = useState({ claim_amount: 45000, claim_frequency: 2, provider_id: 320, diagnosis_code: 180, patient_age: 38, days_since_policy: 120 });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setLoading(true); setError('');
    try {
      const res = await fetch(`${API}/detect-fraud`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form),
      });
      if (!res.ok) { const d = await res.json(); throw new Error(d.detail ?? res.statusText); }
      setResult(await res.json());
    } catch (err: any) { setError(err.message); }
    finally { setLoading(false); }
  };

  const recColor = (r: string) => ({ APPROVE: 'green', REVIEW: 'yellow', REJECT: 'red' }[r] ?? 'blue');

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Panel title="Claim Features">
        <form onSubmit={submit} className="space-y-3">
          {[
            { key: 'claim_amount',      label: 'Claim Amount (KES)'            },
            { key: 'claim_frequency',   label: 'Claims in last 90 days'        },
            { key: 'provider_id',       label: 'Provider ID (numeric)'         },
            { key: 'diagnosis_code',    label: 'ICD-10 Code (numeric)'         },
            { key: 'patient_age',       label: 'Patient Age'                   },
            { key: 'days_since_policy', label: 'Days Since Policy Inception'   },
          ].map(({ key, label }) => (
            <div key={key}>
              <Label>{label}</Label>
              <input type="number" value={(form as any)[key]}
                onChange={e => setForm({ ...form, [key]: Number(e.target.value) })}
                className={inputCls} />
            </div>
          ))}
          <Btn disabled={loading} color="red">{loading ? <><Spinner />Scanning...</> : 'Run Fraud Detection'}</Btn>
        </form>
        {error && <ErrorBox msg={error} />}
      </Panel>

      <Panel title="Fraud Analysis">
        {result ? (
          <div className="space-y-5">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="text-xs font-medium text-[#6b6860]">Recommendation</span>
              <Badge label={result.recommendation} color={recColor(result.recommendation)} />
              {result.is_flagged && <Badge label="FLAGGED" color="red" />}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Card title="Fraud Score"      value={(result.fraud_score * 100).toFixed(1) + '%'} color={result.fraud_score > 0.6 ? 'red' : result.fraud_score > 0.3 ? 'amber' : 'emerald'} />
              <Card title="Fraud Percentage" value={result.fraud_percentage.toFixed(2) + '%'}    color="muted" />
            </div>
            {result.flags.length > 0 ? (
              <div className="border-t border-[#e2e0db] pt-4">
                <p className="text-xs font-semibold text-[#6b6860] uppercase tracking-wide mb-3">Triggered Flags</p>
                <div className="flex flex-wrap gap-2">
                  {result.flags.map((f: string) => <Badge key={f} label={f} color="red" />)}
                </div>
              </div>
            ) : (
              <div className="border-t border-[#e2e0db] pt-4 flex items-center gap-2">
                <span className="text-emerald-600 text-sm">✓</span>
                <p className="text-xs text-emerald-700 font-medium">No rule-based flags triggered</p>
              </div>
            )}
          </div>
        ) : (
          <Empty text="Submit claim features to run Isolation Forest anomaly detection." />
        )}
      </Panel>
    </div>
  );
}

// ─── Tab 4: IBNR Reserving ─────────────────────────────────────────────────────

function IBNRTab() {
  const [useCustom, setUseCustom] = useState(false);
  const [customTriangle, setCustomTriangle] = useState('[[1000,1500,1800,1900],[1200,1750,2100,0],[1400,2000,0,0],[1600,0,0,0]]');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setLoading(true); setError('');
    let payload: any = {};
    if (useCustom) {
      try { payload.triangle = JSON.parse(customTriangle); }
      catch { setError('Invalid JSON triangle matrix.'); setLoading(false); return; }
    }
    try {
      const res = await fetch(`${API}/calculate-ibnr`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
      });
      if (!res.ok) { const d = await res.json(); throw new Error(d.detail ?? res.statusText); }
      setResult(await res.json());
    } catch (err: any) { setError(err.message); }
    finally { setLoading(false); }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Panel title="Claims Development Triangle">
        <form onSubmit={submit} className="space-y-4">
          <div className="flex items-center gap-3">
            <input type="checkbox" id="custom" checked={useCustom} onChange={e => setUseCustom(e.target.checked)}
              className="w-4 h-4 accent-[#0d6e4e] cursor-pointer" />
            <label htmlFor="custom" className="text-xs text-[#6b6860] cursor-pointer font-medium">Use custom triangle (JSON)</label>
          </div>
          {useCustom ? (
            <div>
              <Label>Triangle Matrix (JSON 2D array)</Label>
              <textarea rows={5} value={customTriangle} onChange={e => setCustomTriangle(e.target.value)}
                className={inputCls + ' font-mono resize-none'} />
              <p className="text-xs text-[#9c9890] mt-1">Use 0 for unknown future cells.</p>
            </div>
          ) : (
            <div className="bg-[#f8f7f4] border border-[#e2e0db] rounded-lg p-4 text-xs font-mono">
              <p className="text-[#9c9890] mb-2 font-sans font-medium not-italic">Sample Triangle (AY 2020–2023)</p>
              <pre className="text-[#6b6860] leading-relaxed">{`AY2020  1000  1500  1800  1900\nAY2021  1200  1750  2100     —\nAY2022  1400  2000     —     —\nAY2023  1600     —     —     —`}</pre>
            </div>
          )}
          <Btn disabled={loading} color="violet">{loading ? <><Spinner />Calculating...</> : 'Calculate IBNR Reserves'}</Btn>
        </form>
        {error && <ErrorBox msg={error} />}
      </Panel>

      <Panel title="Chain-Ladder Results">
        {result ? (
          <div className="space-y-5">
            <Card title="Total IBNR Reserve" value={`KES ${result.total_ibnr.toLocaleString()}`} color="violet" />
            <div className="border-t border-[#e2e0db] pt-4">
              <p className="text-xs font-semibold text-[#6b6860] uppercase tracking-wide mb-3">Development Factors</p>
              <div className="flex flex-wrap gap-2">
                {result.development_factors.map((f: number, i: number) => (
                  <span key={i} className="bg-[#f0ede8] border border-[#e2e0db] rounded px-2.5 py-1 text-xs font-mono text-[#1a1a1a]">
                    f{i + 1} = {f.toFixed(4)}
                  </span>
                ))}
              </div>
            </div>
            <div className="border-t border-[#e2e0db] pt-4">
              <p className="text-xs font-semibold text-[#6b6860] uppercase tracking-wide mb-3">IBNR by Accident Year</p>
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-[#e2e0db]">
                    <th className="text-left py-2 font-semibold text-[#6b6860]">Year</th>
                    <th className="text-right py-2 font-semibold text-[#6b6860]">Ultimate (KES)</th>
                    <th className="text-right py-2 font-semibold text-[#6b6860]">IBNR (KES)</th>
                  </tr>
                </thead>
                <tbody>
                  {result.ibnr_by_year.map((ibnr: number, i: number) => (
                    <tr key={i} className="border-b border-[#f0ede8]">
                      <td className="py-2 font-medium text-[#1a1a1a]">AY {2020 + i}</td>
                      <td className="py-2 text-right text-[#6b6860]">{result.projected_ultimates[i].toLocaleString()}</td>
                      <td className="py-2 text-right font-semibold text-[#0d6e4e]">{ibnr.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <Empty text="Run the Chain-Ladder calculation to see IBNR reserve estimates by accident year." />
        )}
      </Panel>
    </div>
  );
}

// ─── Tab 5: Policy RAG ─────────────────────────────────────────────────────────

function PolicyTab() {
  const [query, setQuery] = useState('What is the waiting period for pre-existing conditions?');
  const [topK, setTopK] = useState(3);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [elapsed, setElapsed] = useState(0);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setLoading(true); setError(''); setElapsed(0);
    const start = Date.now();
    const timer = setInterval(() => setElapsed(Math.floor((Date.now() - start) / 1000)), 500);
    try {
      const res = await fetch(`${API}/query-policy`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: topK }),
      });
      if (!res.ok) { const d = await res.json(); throw new Error(d.detail ?? res.statusText); }
      setResult(await res.json());
    } catch (err: any) { setError(err.message); }
    finally { setLoading(false); clearInterval(timer); }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Panel title="Policy Query">
        <form onSubmit={submit} className="space-y-4">
          <div>
            <Label>Natural Language Query</Label>
            <textarea rows={4} value={query} onChange={e => setQuery(e.target.value)}
              className={inputCls + ' resize-none'} />
          </div>
          <div>
            <Label>Top K Results (1–10)</Label>
            <input type="number" min={1} max={10} value={topK}
              onChange={e => setTopK(Number(e.target.value))} className={inputCls} />
          </div>
          <Btn disabled={loading} color="green">
            {loading
              ? <><Spinner />{elapsed > 5 ? `Loading AI model… ${elapsed}s` : 'Searching...'}</>
              : 'Search Policy Documents'}
          </Btn>
          {loading && elapsed > 5 && (
            <p className="text-xs text-[#9c9890] text-center mt-1">
              First search loads the embedding model — subsequent searches will be instant.
            </p>
          )}
        </form>
        {error && <ErrorBox msg={error} />}
      </Panel>

      <Panel title="Matched Policy Clauses">
        {result ? (
          <div className="space-y-4">
            <div className="bg-[#f0faf5] border border-emerald-200 rounded-lg p-4">
              <p className="text-xs font-semibold text-emerald-700 uppercase tracking-wide mb-2">Top Match</p>
              <p className="text-sm text-[#1a1a1a] leading-relaxed">{result.top_match}</p>
            </div>
            {result.matched_clauses.slice(1).map((c: any, i: number) => (
              <div key={i} className="bg-white border border-[#e2e0db] rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-semibold text-[#1a1a1a]">{c.source}</span>
                  <span className="text-xs font-mono text-[#9c9890] bg-[#f8f7f4] px-2 py-0.5 rounded">
                    {c.similarity_score.toFixed(4)}
                  </span>
                </div>
                <p className="text-xs text-[#6b6860] leading-relaxed">{c.clause}</p>
              </div>
            ))}
          </div>
        ) : (
          <Empty text="Enter a natural language query to search the FAISS policy vector index." />
        )}
      </Panel>
    </div>
  );
}

// ─── Root Dashboard ────────────────────────────────────────────────────────────

const TABS = [
  { id: 'health',  label: 'Health Risk'      },
  { id: 'pricing', label: 'Policy Pricing'   },
  { id: 'fraud',   label: 'Fraud Detection'  },
  { id: 'ibnr',    label: 'IBNR Reserving'   },
  { id: 'policy',  label: 'Policy RAG'       },
] as const;

type TabId = typeof TABS[number]['id'];

export default function AfyaRiskDashboard() {
  const [tab, setTab] = useState<TabId>('health');

  return (
    <div className="min-h-screen bg-[#f8f7f4] text-[#1a1a1a] font-sans">

      {/* Header */}
      <header className="bg-white border-b border-[#e2e0db] px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 rounded-lg bg-[#0d6e4e] flex items-center justify-center flex-shrink-0">
              <span className="text-white text-sm font-bold">A</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-[#1a1a1a] tracking-tight">AfyaRisk 2.0</h1>
              <p className="text-xs text-[#9c9890]">Enterprise Actuarial & Insurtech AI Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs text-[#6b6860] bg-[#f8f7f4] border border-[#e2e0db] px-3 py-1.5 rounded-lg hidden sm:flex">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block"></span>
            API live — localhost:8000
          </div>
        </div>
      </header>

      {/* Tab bar */}
      <nav className="bg-white border-b border-[#e2e0db] px-6">
        <div className="max-w-7xl mx-auto flex overflow-x-auto">
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`px-5 py-3.5 text-xs font-semibold border-b-2 whitespace-nowrap transition-colors ${
                tab === t.id
                  ? 'border-[#0d6e4e] text-[#0d6e4e]'
                  : 'border-transparent text-[#6b6860] hover:text-[#1a1a1a] hover:border-[#e2e0db]'
              }`}>
              {t.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {tab === 'health'  && <HealthTab />}
        {tab === 'pricing' && <PricingTab />}
        {tab === 'fraud'   && <FraudTab />}
        {tab === 'ibnr'    && <IBNRTab />}
        {tab === 'policy'  && <PolicyTab />}
      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-6 py-6 border-t border-[#e2e0db] mt-4">
        <p className="text-xs text-[#9c9890]">
          AfyaRisk  · Random Forest · Isolation Forest · Chain-Ladder IBNR · FAISS RAG ·{' '}
          <span className="italic">Prototype — not certified actuarial advice</span>
        </p>
      </footer>
    </div>
  );
}
