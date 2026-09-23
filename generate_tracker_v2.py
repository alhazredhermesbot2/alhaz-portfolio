#!/usr/bin/env python3
"""Self-contained daily ETF tracker generator (readable template embedded)."""
import sys, csv, json
holdings_csv, prices_csv, out_path = sys.argv[1:4]
TEMPLATE = r'''<!DOCTYPE html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ETF Portfolio Tracker - __STAMP__</title>
<style>
  :root{
    color-scheme: light;
    --plane:#f9f9f7; --surface:#fcfcfb;
    --ink:#0b0b0b; --ink2:#52514e; --muted:#898781;
    --grid:#e1e0d9; --axis:#c3c2b7; --border:rgba(11,11,11,0.10);
    --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#eda100; --s5:#7b53d4;
    --fx:#ffd60a; --fxcase:#5c4400;
    --good:#0ca30c; --bad:#d03b3b; --goodink:#006300;
    --chipbg:#f0efec;
  }
  :root[data-theme="dark"]{
    color-scheme: dark;
    --plane:#0d0d0d; --surface:#1a1a19;
    --ink:#ffffff; --ink2:#c3c2b7; --muted:#898781;
    --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,0.10);
    --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#a488e6;
    --fx:#ffe14d; --fxcase:transparent;
    --good:#0ca30c; --bad:#d03b3b; --goodink:#0ca30c;
    --chipbg:#26262400;
  }
  @media (prefers-color-scheme: dark){
    :root[data-theme="auto"]{
      color-scheme: dark;
      --plane:#0d0d0d; --surface:#1a1a19;
      --ink:#ffffff; --ink2:#c3c2b7; --muted:#898781;
      --grid:#2c2c2a; --axis:#383835; --border:rgba(255,255,255,0.10);
      --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --s5:#a488e6;
      --fx:#ffe14d; --fxcase:transparent;
      --goodink:#0ca30c;
    }
  }
  *{box-sizing:border-box}
  body{
    margin:0; background:var(--plane); color:var(--ink);
    font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
    -webkit-font-smoothing:antialiased; line-height:1.45;
  }
  .wrap{max-width:1040px; margin:0 auto; padding:28px 20px 60px}
  header.top{display:flex; align-items:flex-start; justify-content:space-between; gap:16px; flex-wrap:wrap}
  h1{font-size:22px; margin:0 0 4px}
  .sub{color:var(--ink2); font-size:13px; margin:0}
  .toggle{
    border:1px solid var(--border); background:var(--surface); color:var(--ink2);
    border-radius:8px; padding:7px 12px; font-size:13px; cursor:pointer;
  }
  .toggle:hover{color:var(--ink)}

  .tiles{display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:22px 0}
  .tile{background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:16px 16px 14px}
  .tile .lbl{font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; margin:0 0 8px}
  .tile .val{font-size:26px; font-weight:650; letter-spacing:-.01em}
  .tile .val.small{font-size:22px}
  .tile .delta{font-size:13px; margin-top:3px}
  .pos{color:var(--goodink)} .neg{color:var(--bad)}

  .grid2{display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:16px}
  .card{background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:18px}
  .card h2{font-size:14px; margin:0 0 2px}
  .card .cap{font-size:12px; color:var(--muted); margin:0 0 14px}

  /* donut */
  .donutwrap{display:flex; gap:18px; align-items:center; flex-wrap:wrap}
  .donut{flex:0 0 auto}
  .legend{display:flex; flex-direction:column; gap:9px; font-size:13px; min-width:150px}
  .legend .row{display:flex; align-items:center; gap:9px}
  .swatch{width:11px; height:11px; border-radius:3px; flex:0 0 auto}
  .legend .lname{color:var(--ink2)} .legend .lpct{margin-left:auto; font-variant-numeric:tabular-nums; font-weight:600}

  /* pl bars */
  .plrow{display:grid; grid-template-columns:64px 1fr; align-items:center; gap:10px; margin:12px 0; font-size:13px}
  .plrow .tk{font-weight:600}
  .barbox{position:relative; height:22px}
  .barbox .zero{position:absolute; left:50%; top:-3px; bottom:-3px; width:1px; background:var(--axis)}
  .bar{position:absolute; top:2px; height:18px; border-radius:4px}
  .bar .blab{position:absolute; top:50%; transform:translateY(-50%); font-size:11.5px; font-variant-numeric:tabular-nums; white-space:nowrap; color:var(--ink2)}

  /* asset class stacked */
  .stack{display:flex; height:26px; border-radius:6px; overflow:hidden; gap:2px; margin-top:2px}
  .stack .seg{display:flex; align-items:center; justify-content:center; font-size:11.5px; color:#fff; font-weight:600}
  .classlegend{display:flex; gap:16px; flex-wrap:wrap; font-size:12.5px; color:var(--ink2); margin-top:10px}
  .classlegend .row{display:flex; align-items:center; gap:7px}

  table{width:100%; border-collapse:collapse; font-size:13px; margin-top:4px}
  th,td{padding:10px 10px; text-align:right; border-bottom:1px solid var(--grid); font-variant-numeric:tabular-nums}
  th{color:var(--muted); font-weight:600; font-size:11.5px; text-transform:uppercase; letter-spacing:.03em; border-bottom:1px solid var(--axis)}
  th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){text-align:left; font-variant-numeric:normal}
  td.tk{font-weight:650}
  td .nm{color:var(--ink2); font-size:12px}
  tr.total td{border-bottom:none; border-top:2px solid var(--axis); font-weight:700; padding-top:12px}
  input.px{
    width:74px; text-align:right; font:inherit; font-variant-numeric:tabular-nums;
    background:var(--plane); color:var(--ink); border:1px solid var(--border);
    border-radius:6px; padding:5px 7px;
  }
  input.px:focus{outline:2px solid var(--s1); outline-offset:-1px; border-color:var(--s1)}
  /* performance chart */
  .perfwrap{position:relative}
  .perf-legend{display:flex; gap:16px; flex-wrap:wrap; font-size:12.5px; margin:2px 0 12px}
  .perf-legend .row{display:flex; align-items:center; gap:7px; color:var(--ink2)}
  .perf-legend .row.tot{font-weight:650; color:var(--ink)}
  .perf-legend .ln{width:16px; height:0; border-top-width:2px; border-top-style:solid; flex:0 0 auto}
  .perf-legend .fxnote{color:var(--muted); font-size:11.5px; font-weight:400}
  /* Same problem as the chart line: a bright-yellow 2px rule disappears on the
     light card, so the casing colour is drawn as an outline behind the swatch. */
  .perf-legend .ln.fx{outline:1px solid var(--fxcase)}
  .perf-tip{position:absolute; pointer-events:none; background:var(--surface); border:1px solid var(--border);
    border-radius:8px; padding:8px 10px; font-size:12px; box-shadow:0 4px 14px rgba(0,0,0,.14); opacity:0;
    transition:opacity .08s; min-width:132px; z-index:5}
  .perf-tip .d{color:var(--muted); font-size:11px; margin-bottom:5px}
  .perf-tip .r{display:flex; align-items:center; gap:7px; margin:2px 0}
  .perf-tip .r .sw{width:9px;height:9px;border-radius:2px;flex:0 0 auto}
  .perf-tip .r .nm{color:var(--ink2)} .perf-tip .r .v{margin-left:auto; font-variant-numeric:tabular-nums; font-weight:600}
  .perf-toggle{display:inline-flex;gap:0;border:1px solid var(--border);border-radius:8px;overflow:hidden;margin-bottom:8px}
  .perf-toggle button{background:transparent;border:none;color:var(--ink2);font-size:12px;padding:5px 14px;cursor:pointer;font-weight:500;line-height:1.5}
  .perf-toggle button.active{background:var(--s1);color:#fff}
  .perf-toggle button:hover:not(.active){color:var(--ink)}
  .note{font-size:12px;color:var(--muted);margin-top:16px;line-height:1.6}
  .dot{display:inline-block; width:9px; height:9px; border-radius:2px; vertical-align:baseline}
  @media (max-width:760px){
    .tiles{grid-template-columns:repeat(2,1fr)}
    .grid2{grid-template-columns:1fr}
    .hidem{display:none}
  }
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div>
      <h1>ETF Portfolio Tracker - __STAMP__</h1>
      <p class="sub">CMC Markets Invest · Account 1089557 · reconstructed from trade confirmations</p>
    </div>
    <button class="toggle" id="themeBtn">◐ Theme</button>
  </header>

  <section class="tiles">
    <div class="tile"><p class="lbl">Portfolio value</p><div class="val" id="tVal">—</div><div class="delta" id="tValDelta"></div></div>
    <div class="tile"><p class="lbl">Invested</p><div class="val small" id="tCost">—</div><div class="delta" style="color:var(--muted)">cost basis</div></div>
    <div class="tile"><p class="lbl">Total P / L</p><div class="val small" id="tPL">—</div><div class="delta" id="tPLpct"></div></div>
    <div class="tile"><p class="lbl">Holdings</p><div class="val" id="tCount">—</div><div class="delta" style="color:var(--muted)">ETFs</div></div>
  </section>

  <div class="card" style="margin-bottom:16px">
    <h2>Performance over time</h2>
    <p class="cap" id="perfCap">Unrealised return vs. average cost, since 3 Jun 2026 — individual holdings and overall</p>
    <div class="perf-toggle" id="perfToggle">
      <button id="dwBtn" class="active">Dollar-weighted</button>
      <button id="twBtn">Time-weighted</button>
    </div>
    <div class="perf-legend" id="perfLegend"></div>
    <div class="perfwrap" id="perfWrap">
      <svg id="perf" width="100%" viewBox="0 0 900 340" role="img" aria-label="Performance over time line chart" style="display:block"></svg>
      <div class="perf-tip" id="perfTip"></div>
    </div>
    <p class="note" style="margin-top:10px">Each coloured line is a holding's price ÷ your average cost − 1, so its endpoint equals that holding's P/L% in the table below. The <strong>Overall</strong> line is a <strong>time-weighted return</strong>: it chains the daily return of the units you <em>actually held each day</em> (from your trade ledger), so it reflects your real holdings over time and removes the distortion of <em>when</em> you added money. It begins at your first purchase (3 Jun 2026) and, being time-weighted, won't equal the table's total P/L% (that figure is money-weighted). Daily ASX closes via Hermes/yfinance.</p>
  </div>

  __VALUE_CHART_CARD__<div class="grid2">
    <div class="card">
      <h2>Allocation by value</h2>
      <p class="cap">Share of current portfolio value</p>
      <div class="donutwrap">
        <svg class="donut" id="donut" width="176" height="176" viewBox="0 0 176 176" role="img" aria-label="Allocation donut chart"></svg>
        <div class="legend" id="donutLegend"></div>
      </div>
    </div>
    <div class="card">
      <h2>Profit / loss by holding</h2>
      <p class="cap">Unrealised return vs. entry price (%)</p>
      <div id="plbars"></div>
    </div>
  </div>

  <div class="card" style="margin-bottom:16px">
    <h2>Asset mix</h2>
    <p class="cap">Equities vs. commodity exposure</p>
    <div class="stack" id="classStack"></div>
    <div class="classlegend" id="classLegend"></div>
  </div>

  <div class="card">
    <h2>Holdings</h2>
    <p class="cap">Edit the <strong>Current price</strong> cells to refresh values — everything recalculates live.</p>
    <table>
      <thead>
        <tr>
          <th>Ticker</th><th class="hidem">Name</th><th>Units</th>
          <th>Entry</th><th>Current</th><th>Value</th>
          <th>Weight</th><th>P/L $</th><th>P/L %</th>
        </tr>
      </thead>
      <tbody id="tbody"></tbody>
      <tfoot id="tfoot"></tfoot>
    </table>
    <p class="note" id="footnote"></p>
  </div>
</div>

<script>
const AUD = n => (n<0?'-':'') + '$' + Math.abs(n).toLocaleString('en-AU',{minimumFractionDigits:2,maximumFractionDigits:2});
const PCT = n => (n>0?'+':'') + n.toFixed(1) + '%';

// Holdings reconstructed from CMC trade confirmations (units) + portfolio.csv (prices).
const holdings = __HOLDINGS__;
// Daily ASX closes (AUD), from account open through latest — source: Hermes / yfinance.
// Column order is [date, IVV, PMGOLD, VGE, VEQ, VGS]. The source etf_prices CSV uses
// header order Date,IVV,PMGOLD,VEQ,VGE,VGS; the generator maps each ticker to its
// column by matching the latest close against the holdings current price, so output is
// always emitted in this canonical order regardless of the CSV's column order.
const PRICES = __PRICES__;
// Time-weighted-return series for the Overall line (null unless portfolio.json supplied).
// Aligned 1:1 with PRICES rows; chains the daily return of the units actually held each day.
const OVERALL_TWR = __OVERALL_TWR__;
const DW_OVERALL = __DW_OVERALL__;           // dollar-weighted aggregate (View 1 Overall)
const TW_PER_HOLDING = __TW_PER_HOLDING__;    // {IVV: [...], PMGOLD: [...], ...} — price/series_start (View 2 per-holding)
const DW_PER_HOLDING = __DW_PER_HOLDING__;    // {IVV: [...], PMGOLD: [...], ...} — running-cost-basis P/L per holding (View 1 per-holding)
const FIRST_PURCHASE_IDX = __FIRST_PURCHASE_IDX__; // {IVV: 0, PMGOLD: 0, ...} — index into PRICES at first buy
// AUD/USD overlay, as % change from a base, INVERTED so the line rises as the
// AUD weakens — the direction that co-moves with AUD returns on foreign assets.
// Two series because the chart has two baselines: FX_TW is based at index 0 to
// match TW_PER_HOLDING's shared day-0 baseline; FX_DW is based at DW_OVERALL's
// first non-null day so it spans the same window the dollar-weighted Overall
// line does. Aligned 1:1 with PRICES. null entries are real gaps — never 0.
const FX_TW = __FX_TW__;
const FX_DW = __FX_DW__;
let perfMode = 'dw'; // 'dw' | 'tw'
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

// ---- performance-over-time line chart (individual + overall) ----
function drawPerf(){
  const svg=document.getElementById('perf'); if(!svg) return;
  const order=['IVV','PMGOLD','VGE','VEQ','VGS'];
  const H_=order.map(tk=>holdings.find(h=>h.tk===tk));
  const costTot=holdings.reduce((s,h)=>s+h.units*h.entry,0);
  const mon=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const isDW=perfMode==='dw';
  let series,overall;
  if(isDW && DW_OVERALL){
    series=H_.map((h,i)=>({tk:h.tk,color:css(h.cvar),
      vals:(DW_PER_HOLDING&&DW_PER_HOLDING[h.tk])||[]}));
    overall={tk:'Overall',color:css('--ink'),tot:true,vals:DW_OVERALL};
  }else if(!isDW && TW_PER_HOLDING && OVERALL_TWR){
    series=H_.map((h,i)=>({tk:h.tk,color:css(h.cvar),
      vals:TW_PER_HOLDING[h.tk]||[]}));
    overall={tk:'Overall',color:css('--ink'),tot:true,vals:OVERALL_TWR};
  }else{
    series=H_.map((h,i)=>({tk:h.tk,color:css(h.cvar),
      vals:PRICES.map(r=>{const v=r[i+1];return v!=null?(v/h.entry-1)*100:null;})}));
    overall={tk:'Overall',color:css('--ink'),tot:true,
      vals:OVERALL_TWR?OVERALL_TWR:PRICES.map(r=>((H_.reduce((s,h,i)=>s+h.units*r[i+1],0))/costTot-1)*100)};
  }
  // The FX overlay is a driver, not a holding, and is deliberately absent from
  // every aggregate: `overall` above, `costTot`, and the value chart's
  // series.reduce all iterate the holdings and never see it. It joins `all`
  // only for autoscale, legend, end-labels and hover — presentation, not
  // arithmetic. (Autoscale is safe: over the current window FX spans about
  // -0.4%..+4.3% against an existing envelope of roughly -10%..+7.4%, so it
  // does not widen the range or compress the other lines.)
  const fxVals=(isDW&&DW_OVERALL&&FX_DW)?FX_DW:FX_TW;
  const fx=(fxVals&&fxVals.some(v=>v!=null))
    ?{tk:'Currency effect',color:css('--fx'),fx:true,vals:fxVals}:null;
  const all=fx?[...series,overall,fx]:[...series,overall];
  const n=PRICES.length;
  let lo=0,hi=0;
  all.forEach(s=>s.vals.forEach(v=>{if(v!=null){lo=Math.min(lo,v);hi=Math.max(hi,v);}}));
  const pad=(hi-lo)*0.12||1;lo-=pad;hi+=pad;
  const W=900,H=340,padL=44,padR=58,padT=16,padB=30;
  const plotW=W-padL-padR,plotH=H-padT-padB;
  const X=i=>padL+(n===1?0:i/(n-1)*plotW);
  const Y=v=>padT+(hi-v)/(hi-lo)*plotH;
  const gc=css('--grid'),axc=css('--axis'),mut=css('--muted');
  let g='';
  // y gridlines
  const steps=5;
  for(let k=0;k<=steps;k++){
    const v=lo+(hi-lo)*k/steps,y=Y(v);
    const zero=Math.abs(v)<1e-9;
    g+=`<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W-padR}" y2="${y.toFixed(1)}" stroke="${zero?axc:gc}" stroke-width="${zero?1.4:1}"/>`;
    g+=`<text x="${padL-8}" y="${(y+3.5).toFixed(1)}" text-anchor="end" font-size="11" fill="${mut}">${v>0?'+':''}${v.toFixed(1)}%</text>`;
  }
  // x ticks
  const ticks=[0,Math.round((n-1)*0.25),Math.round((n-1)*0.5),Math.round((n-1)*0.75),n-1];
  [...new Set(ticks)].forEach(i=>{
    const d=PRICES[i][0].split('-');const lab=parseInt(d[2],10)+' '+mon[+d[1]-1];
    g+=`<text x="${X(i).toFixed(1)}" y="${H-10}" text-anchor="middle" font-size="11" fill="${mut}">${lab}</text>`;
  });
  // path helper that skips nulls
  const pathSeg=(varr,from,to)=>{let p='';for(let i=from;i<=to;i++){
    const v=varr[i];if(v==null)continue;
    p+=`${p?'L':'M'}${X(i).toFixed(1)} ${Y(v).toFixed(1)}`;
  }return p;};
  // pathSeg bridges an interior null (it just continues the same subpath).
  // The FX series must BREAK at one instead: the RBA publishes no fix on NSW
  // bank holidays that the ASX trades through (2026-08-03 is one), and drawing
  // straight through that gap would assert a rate that was never observed.
  // A null starts a fresh subpath; it is never coerced to 0 or carried forward.
  const pathBreak=varr=>{let p='',pen=false;for(let i=0;i<n;i++){
    const v=varr[i];
    if(v==null){pen=false;continue;}
    p+=`${pen?'L':'M'}${X(i).toFixed(1)} ${Y(v).toFixed(1)}`;pen=true;
  }return p;};
  // render lines: View 2 gets dashed un-owned stretch
  if(!isDW && TW_PER_HOLDING && FIRST_PURCHASE_IDX){
    series.forEach((s,j)=>{
      const fpIdx=FIRST_PURCHASE_IDX[s.tk]||0;
      const col=s.color;
      if(fpIdx>0){
        const pre=pathSeg(s.vals,0,fpIdx);
        if(pre) g+=`<path d="${pre}" fill="none" stroke="${col}" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="5,4" opacity="0.40"/>`;
      }
      const post=pathSeg(s.vals,Math.max(fpIdx,0),n-1);
      if(post) g+=`<path d="${post}" fill="none" stroke="${col}" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round" opacity="0.95"/>`;
      if(fpIdx<n){
        const mv=s.vals[fpIdx];if(mv!=null) g+=`<circle cx="${X(fpIdx).toFixed(1)}" cy="${Y(mv).toFixed(1)}" r="4" fill="${col}" stroke="${css('--surface')}" stroke-width="1.5"/>`;
      }
    });
  }else{
    series.forEach(s=>{const p=pathSeg(s.vals,0,n-1);if(p) g+=`<path d="${p}" fill="none" stroke="${s.color}" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round" opacity="0.95"/>`;});
  }
  // Dashed: FX is a different kind of series and the dash says so at a glance.
  // Drawn before Overall so the thick --ink line stays legible on top.
  if(fx){
    const fp=pathBreak(fx.vals);
    if(fp){
      // Bright yellow cannot reach 3:1 against the light theme's near-white card
      // (it tops out near 1.4:1), so on that theme a darker casing is drawn
      // underneath at greater width. The visible colour stays bright yellow; the
      // casing only supplies the edge. On dark, yellow already scores ~12:1, so
      // --fxcase is transparent and this costs nothing. Same `d` and dasharray,
      // so the casing dashes register exactly with the yellow ones.
      const fxCase=css('--fxcase');
      if(fxCase&&fxCase!=='transparent'){
        g+=`<path d="${fp}" fill="none" stroke="${fxCase}" stroke-width="3.8" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="7,4" opacity="0.95"/>`;
      }
      g+=`<path d="${fp}" fill="none" stroke="${fx.color}" stroke-width="1.9" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="7,4" opacity="1"/>`;
    }
  }
  const op=pathSeg(overall.vals,0,n-1);
  if(op) g+=`<path d="${op}" fill="none" stroke="${overall.color}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>`;
  // end labels
  all.forEach(s=>{
    let i=n-1;while(i>=0&&s.vals[i]==null)i--;
    if(i<0)return;
    const v=s.vals[i],y=Y(v);
    // 11px bright-yellow text on near-white is illegible, so on the light theme
    // the FX end-label is painted in the casing colour instead of the line colour.
    const fxc=css('--fxcase');
    const labCol=(s.fx&&fxc&&fxc!=='transparent')?fxc:s.color;
    g+=`<text x="${W-padR+6}" y="${(y+3.5).toFixed(1)}" font-size="11" font-weight="${s.tot?'700':'600'}" fill="${labCol}">${v>0?'+':''}${v.toFixed(1)}%</text>`;
  });
  g+=`<line id="perfCross" x1="0" y1="${padT}" x2="0" y2="${padT+plotH}" stroke="${axc}" stroke-width="1" opacity="0"/>`;
  all.forEach((s,idx)=>{g+=`<circle id="pd${idx}" r="3.5" fill="${s.color}" stroke="${css('--surface')}" stroke-width="1.5" opacity="0"/>`;});
  g+=`<rect id="perfHit" x="${padL}" y="${padT}" width="${plotW}" height="${plotH}" fill="transparent"/>`;
  svg.innerHTML=g;
  // legend
  document.getElementById('perfLegend').innerHTML=
    all.map(s=>{
      // 0.716 is the familiar AUD/USD quote; this line is its reciprocal, so
      // say which way is which rather than leaving it to be re-derived later.
      const note=s.fx
        ?` <span class="fxnote">&uarr; = AUD weaker${isDW?' &middot; based with Overall':''}</span>`:'';
      return `<div class="row ${s.tot?'tot':''}"><span class="ln${s.fx?' fx':''}" style="border-top-color:${s.color};${s.tot?'border-top-width:3px':''}${s.fx?';border-top-style:dashed':''}"></span>${s.tk}${note}</div>`;
    }).join('');
  // caption + footnote update
  const cap=document.getElementById('perfCap');
  if(cap){
    if(isDW){
      cap.textContent='Dollar-weighted: each line is price ÷ the running cost of the lots you actually held that day − 1, so it shows your real P/L at each point in time. The Overall line aggregates this across positions — its endpoint equals the P/L tile above. The dashed Currency effect line (up = AUD weaker) is based at the same day as Overall, not at each holding\'s own first purchase, so compare it with Overall rather than with the individual holdings.';
    }else{
      cap.textContent='Time-weighted: each line is price ÷ price at series start − 1. Faint sections precede your first purchase of that holding. The Overall line chains daily returns of the units you actually held. The dashed Currency effect line (up = AUD weaker) shares that day-0 baseline, so it decomposes the currency factor common to all five holdings.';
    }
  }
  const fn=document.querySelector('.card .note');
  if(fn){
    if(isDW){
      fn.innerHTML='The dashed <strong>Currency effect</strong> line is the currency factor, and it <strong>rises when the AUD weakens</strong>: every holding here is unhedged foreign-currency exposure, so a weaker AUD adds to the AUD value of all five &mdash; holding their local-currency prices constant. Day to day it often moves opposite to them anyway, because a stronger USD tends to push those underlying prices down at the same time; that gap between the two is the point of showing it. It is the AUD/USD quote <em>inverted</em>, shown as % change from the same baseline as the other lines, so it reads as the currency\'s own contribution to your return rather than as an exchange rate. Sampled at the <strong>WM/Reuters 4pm Sydney fix</strong> (RBA table F11.1), the same instant as the ASX close, so the two series measure the same moment. It breaks on days the RBA published no fix. Explanatory only. '+'Each line is a holding\'s price ÷ its <strong>running cost basis</strong> (the fill-price-weighted cost of the lots you held on each day) − 1, so it shows your P/L as it was at the time rather than today\'s average cost projected backwards. Its endpoint still equals that holding\'s P/L% in the table. The <strong>Overall</strong> line is the same dollar-weighted aggregate across positions — it agrees with the P/L tile above. Daily ASX closes via Hermes/yfinance.';
    }else{
      fn.innerHTML='The dashed <strong>Currency effect</strong> line is the currency factor, and it <strong>rises when the AUD weakens</strong>: every holding here is unhedged foreign-currency exposure, so a weaker AUD adds to the AUD value of all five &mdash; holding their local-currency prices constant. Day to day it often moves opposite to them anyway, because a stronger USD tends to push those underlying prices down at the same time; that gap between the two is the point of showing it. It is the AUD/USD quote <em>inverted</em>, shown as % change from the same baseline as the other lines, so it reads as the currency\'s own contribution to your return rather than as an exchange rate. Sampled at the <strong>WM/Reuters 4pm Sydney fix</strong> (RBA table F11.1), the same instant as the ASX close, so the two series measure the same moment. It breaks on days the RBA published no fix. Explanatory only. '+'Each line is a holding\'s price ÷ price at the series start (3 Jun 2026) − 1, measured on a shared baseline for fair comparison. <strong>Faint dashed sections</strong> precede your first purchase of that holding. The <strong>Overall</strong> line is a <strong>time-weighted return</strong> chained from daily returns of the units you actually held — it removes the distortion of <em>when</em> you added money. Daily ASX closes via Hermes/yfinance.';
    }
  }
  // hover behaviour
  const tip=document.getElementById('perfTip'),cross=document.getElementById('perfCross'),wrap=document.getElementById('perfWrap');
  const dots=all.map((_,idx)=>document.getElementById('pd'+idx));
  function move(clientX){
    const rect=svg.getBoundingClientRect();
    const vx=(clientX-rect.left)/rect.width*W;
    let i=Math.round((vx-padL)/plotW*(n-1));i=Math.max(0,Math.min(n-1,i));
    const xU=X(i);
    cross.setAttribute('x1',xU);cross.setAttribute('x2',xU);cross.setAttribute('opacity','1');
    all.forEach((s,idx)=>{const v=s.vals[i];if(v!=null){dots[idx].setAttribute('cx',xU);dots[idx].setAttribute('cy',Y(v));dots[idx].setAttribute('opacity','1');}else{dots[idx].setAttribute('opacity','0');}});
    const d=PRICES[i][0].split('-');const dlab=parseInt(d[2],10)+' '+mon[+d[1]-1]+' '+d[0];
    tip.innerHTML=`<div class="d">${dlab}</div>`+
      all.map(s=>{
        const fc=css('--fxcase');
        const swSty=`background:${s.color}`+((s.fx&&fc&&fc!=='transparent')?`;outline:1px solid ${fc}`:'');
        return `<div class="r"><span class="sw" style="${swSty}"></span><span class="nm">${s.tk}</span><span class="v" style="color:${s.tot?css('--ink'):'inherit'}">${s.vals[i]!=null?(s.vals[i]>0?'+':'')+s.vals[i].toFixed(2)+'%':'—'}</span></div>`;
      }).join('');
    tip.style.opacity='1';
    const xpx=xU/W*rect.width;
    let left=xpx+14;if(left>wrap.clientWidth-150)left=xpx-tip.offsetWidth-14;
    tip.style.left=Math.max(0,left)+'px'; tip.style.top='6px';
  }
  svg.addEventListener('mousemove',e=>move(e.clientX));
  svg.addEventListener('mouseleave',()=>{tip.style.opacity='0';cross.setAttribute('opacity','0');dots.forEach(d=>d.setAttribute('opacity','0'));});
  svg.addEventListener('touchmove',e=>{if(e.touches[0])move(e.touches[0].clientX);},{passive:true});
}
// ---- toggle wiring ----
const dwBtn=document.getElementById('dwBtn'),twBtn=document.getElementById('twBtn');
if(dwBtn&&twBtn){
  dwBtn.addEventListener('click',()=>{perfMode='dw';dwBtn.classList.add('active');twBtn.classList.remove('active');drawPerf();});
  twBtn.addEventListener('click',()=>{perfMode='tw';twBtn.classList.add('active');dwBtn.classList.remove('active');drawPerf();});
}

function calc(){
  let val=0, cost=0;
  holdings.forEach(h=>{ h.value=h.units*h.price; h.cost=h.units*h.entry; h.pl=h.value-h.cost; h.plpct=h.cost?h.pl/h.cost*100:0; val+=h.value; cost+=h.cost; });
  holdings.forEach(h=> h.weight = val? h.value/val*100 : 0);
  return {val, cost, pl:val-cost, plpct: cost?(val-cost)/cost*100:0};
}

function render(){
  const t = calc();
  // tiles
  tVal.textContent = AUD(t.val);
  const dv = document.getElementById('tValDelta');
  dv.textContent = (t.pl>=0?'▲ ':'▼ ') + AUD(t.pl) + ' all-time';
  dv.className = 'delta ' + (t.pl>=0?'pos':'neg');
  tCost.textContent = AUD(t.cost);
  tPL.textContent = AUD(t.pl); tPL.className = 'val small ' + (t.pl>=0?'pos':'neg');
  const dp = document.getElementById('tPLpct'); dp.textContent = PCT(t.plpct); dp.className='delta '+(t.pl>=0?'pos':'neg');
  tCount.textContent = holdings.length;

  // donut
  const R=74, C=88, sw=20, circ=2*Math.PI*R, gap=6; // px gap between segments
  let off=0; const svg=document.getElementById('donut'); svg.innerHTML='';
  svg.insertAdjacentHTML('beforeend',`<circle cx="${C}" cy="${C}" r="${R}" fill="none" stroke="${css('--grid')}" stroke-width="${sw}"/>`);
  holdings.forEach(h=>{
    const len=Math.max(0, h.weight/100*circ - gap);
    svg.insertAdjacentHTML('beforeend',
      `<circle cx="${C}" cy="${C}" r="${R}" fill="none" stroke="${css(h.cvar)}" stroke-width="${sw}"
        stroke-dasharray="${len} ${circ-len}" stroke-dashoffset="${-off}"
        transform="rotate(-90 ${C} ${C})" stroke-linecap="butt"><title>${h.tk} ${h.weight.toFixed(1)}%</title></circle>`);
    off += h.weight/100*circ;
  });
  svg.insertAdjacentHTML('beforeend',
    `<text x="${C}" y="${C-4}" text-anchor="middle" font-size="12" fill="${css('--muted')}">Value</text>
     <text x="${C}" y="${C+16}" text-anchor="middle" font-size="17" font-weight="650" fill="${css('--ink')}">${AUD(t.val).replace('.00','')}</text>`);
  // donut legend
  document.getElementById('donutLegend').innerHTML = holdings.map(h=>
    `<div class="row"><span class="swatch" style="background:${css(h.cvar)}"></span><span class="lname">${h.tk}</span><span class="lpct">${h.weight.toFixed(1)}%</span></div>`
  ).join('');

  // pl bars
  const maxAbs = Math.max(5, ...holdings.map(h=>Math.abs(h.plpct)));
  document.getElementById('plbars').innerHTML = holdings.map(h=>{
    const w = Math.abs(h.plpct)/maxAbs*46; // percent of half-width (headroom left for labels)
    const col = h.pl>=0?css('--good'):css('--bad');
    const side = h.pl>=0 ? `left:50%; width:${w}%;` : `right:50%; width:${w}%;`;
    // label sits in the empty half, just across the zero line — always has room, never clips
    const lab = h.pl>=0
      ? `<span class="blab" style="right:calc(50% + 8px); text-align:right">${PCT(h.plpct)}</span>`
      : `<span class="blab" style="left:calc(50% + 8px)">${PCT(h.plpct)}</span>`;
    return `<div class="plrow"><span class="tk">${h.tk}</span>
      <div class="barbox"><div class="zero"></div><div class="bar" style="${side} background:${col}"></div>${lab}</div></div>`;
  }).join('');

  // asset class stack
  const classes={}; holdings.forEach(h=> classes[h.cls]=(classes[h.cls]||0)+h.value);
  const clsColors={Equities:'--s1', Gold:'--s2'};
  const stack=document.getElementById('classStack'); stack.innerHTML='';
  Object.entries(classes).forEach(([k,v])=>{
    const pc=v/t.val*100;
    stack.insertAdjacentHTML('beforeend',`<div class="seg" style="flex:${pc}; background:${css(clsColors[k]||'--s3')}">${pc.toFixed(0)}%</div>`);
  });
  document.getElementById('classLegend').innerHTML = Object.entries(classes).map(([k,v])=>
    `<div class="row"><span class="dot" style="background:${css(clsColors[k]||'--s3')}"></span>${k} — ${AUD(v)} (${(v/t.val*100).toFixed(1)}%)</div>`
  ).join('');

  // table
  document.getElementById('tbody').innerHTML = holdings.map((h,i)=>`
    <tr>
      <td class="tk">${h.tk}</td>
      <td class="hidem"><span class="nm">${h.nm}</span></td>
      <td>${h.units}</td>
      <td>${AUD(h.entry)}</td>
      <td><input class="px" type="number" step="0.01" min="0" value="${h.price.toFixed(2)}" data-i="${i}" aria-label="Current price ${h.tk}"></td>
      <td>${AUD(h.value)}</td>
      <td>${h.weight.toFixed(1)}%</td>
      <td class="${h.pl>=0?'pos':'neg'}">${AUD(h.pl)}</td>
      <td class="${h.pl>=0?'pos':'neg'}">${PCT(h.plpct)}</td>
    </tr>`).join('');
  document.getElementById('tfoot').innerHTML = `
    <tr class="total">
      <td>TOTAL</td><td class="hidem"></td><td></td><td></td><td></td>
      <td>${AUD(t.val)}</td><td>100%</td>
      <td class="${t.pl>=0?'pos':'neg'}">${AUD(t.pl)}</td>
      <td class="${t.pl>=0?'pos':'neg'}">${PCT(t.plpct)}</td>
    </tr>`;

  document.querySelectorAll('input.px').forEach(inp=>{
    inp.addEventListener('change', e=>{
      const v=parseFloat(e.target.value); if(!isNaN(v)&&v>=0){ holdings[+e.target.dataset.i].price=v; render(); }
    });
  });

  document.getElementById('footnote').innerHTML =
    `Units are exact, reconstructed from your 10 CMC trade confirmations (all BUY orders, 29 May–6 Aug 2026). `+
    `Entry prices are the average cost per unit; values recompute as units × price. Prices are indicative — edit the Current column to update.`;

  drawPerf();
}

// theme toggle: auto -> light -> dark -> auto
const btn=document.getElementById('themeBtn'); const root=document.documentElement;
btn.addEventListener('click',()=>{
  const cur=root.getAttribute('data-theme');
  const next = cur==='auto'?'light':cur==='light'?'dark':'auto';
  root.setAttribute('data-theme',next);
  btn.textContent = next==='auto'?'◐ Auto':next==='light'?'☀ Light':'☾ Dark';
  render();
});
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{ if(root.getAttribute('data-theme')==='auto') render(); });
render();
</script>
__VALUE_CHART_SCRIPT__</body>
</html>
'''


# static per-ticker metadata (not in the CSVs)
META = {
 'IVV':    {'nm':'iShares S&P 500 (AUD)',          'cls':'Equities', 'cvar':'--s1'},
 'PMGOLD': {'nm':'Perth Mint Gold',                 'cls':'Gold',     'cvar':'--s2'},
 'VGE':    {'nm':'Vanguard FTSE Emerging Markets',  'cls':'Equities', 'cvar':'--s3'},
 'VEQ':    {'nm':'Vanguard FTSE Europe',            'cls':'Equities', 'cvar':'--s4'},
 'VGS':    {'nm':'Vanguard MSCI Intl Shares',        'cls':'Equities', 'cvar':'--s5'},
}
ORDER = ['IVV','PMGOLD','VGE','VEQ','VGS']
# Columns in the price CSV that are NOT holdings. The self-correcting mapper
# below pairs each ticker with a price column by matching that column's last
# value against the ticker's current price, and it walks EVERY non-Date column
# to do it. AUDUSD (~0.72) cannot collide with today's prices (61–160), but
# that is luck, not a guarantee — a future non-price column, or a holding that
# ever trades near the FX rate, would silently bind a ticker to the wrong
# column. Exclude non-holding columns by name instead of relying on the gap.
NON_TICKER_COLS = {'AUDUSD'}
FX_COL = 'AUDUSD'

def num(x):
    x=(x or '').strip()
    return float(x) if x not in ('','None') else None

# --- holdings ---
hold={}
with open(holdings_csv, newline='') as f:
    for row in csv.DictReader(f):
        tk=(row.get('Ticker') or '').strip()
        if tk in META:
            hold[tk]={'units':num(row['Units']),'entry':num(row['Entry Price (AUD)']),
                      'current':num(row['Current Price (AUD)'])}
for tk in ORDER:
    if tk not in hold: raise SystemExit(f"Holdings CSV missing {tk}")

# --- prices ---
with open(prices_csv, newline='') as f:
    rows=list(csv.reader(f))
header=[h.strip() for h in rows[0]]
data=[r for r in rows[1:] if r and r[0].strip()]
cols={header[i]: [num(r[i]) for r in data] for i in range(len(header)) if header[i]!='Date'}
dates=[r[0].strip() for r in data]

# --- self-correcting map: ticker -> price column by matching latest close to holdings current ---
notes=[]
avail=[c for c in header if c!='Date' and c not in NON_TICKER_COLS]
last={c:cols[c][-1] for c in avail}
mapping={}
used=set()
for tk in ORDER:
    cur=hold[tk]['current']
    match=None
    for c in avail:
        if c in used: continue
        if last[c] is not None and cur is not None and abs(last[c]-cur)<0.01:
            match=c; break
    if match is None:               # fallback: same-name column
        match=tk if tk in cols else None
        if match: notes.append(f"{tk}: no price-column matched current {cur}; fell back to name '{match}'")
    mapping[tk]=match
    if match: used.add(match)
    if match and match!=tk:
        notes.append(f"AUTO-CORRECT: '{tk}' data taken from column '{match}' (labels were crossed)")

# --- build canonical PRICES rows [date, IVV, PMGOLD, VGE, VEQ] ---
prices=[]
for i,d in enumerate(dates):
    prices.append([d]+[round(cols[mapping[tk]][i],2) if mapping[tk] and cols[mapping[tk]][i] is not None else None for tk in ORDER])

# --- AUD/USD overlay series (% change from a base, inverted) -------------
# Plotted as the reciprocal of the AUD/USD quote so the line RISES as the AUD
# weakens — the direction that co-moves with AUD-denominated returns on foreign
# assets. Expressed as % change from a base so it shares units with every other
# series on the chart.
#
#   pct[i] = (1/fx[i]) / (1/fx[base]) - 1 = fx[base]/fx[i] - 1
#
# Nulls propagate as nulls. They are never forward-filled and never coerced to
# 0: on the chart path a 0 would read as "the AUD did not move", which is a
# claim the data does not make. (This is the same class of bug that rendered
# gold at $0 and overall at -100% before v1.7.1.)
fx_raw = cols.get(FX_COL) if FX_COL in cols else None

def _fx_pct(base_i, clip_before_base=False):
    """FX series as % from `base_i`, or None if unusable.

    clip_before_base nulls everything left of the baseline. Used in DW mode:
    there DW_OVERALL itself is null until the first purchase, so an FX line
    running back to day 0 would be the only thing on the chart covering that
    stretch — implying a comparison that has no counterpart, which is the same
    error as basing it there. In TW mode every holding IS drawn from day 0
    (faint before its first purchase), so the FX line runs the full width too.
    """
    if not fx_raw or base_i is None or base_i >= len(fx_raw):
        return None
    # The baseline day itself may be a gap (bank holiday); step forward to the
    # first observed fix at or after it rather than giving up or reaching back
    # to a day outside the intended window.
    b = None
    for k in range(base_i, len(fx_raw)):
        if fx_raw[k]:
            b = fx_raw[k]
            break
    if not b:
        return None
    return [None if (clip_before_base and i < base_i)
            else (round((b / v - 1) * 100, 4) if v else None)
            for i, v in enumerate(fx_raw)]

FX_TW_JS = 'null'
FX_DW_JS = 'null'
_fx_tw = _fx_pct(0)          # TW: shared day-0 baseline, matching TW_PER_HOLDING
if _fx_tw is not None:
    FX_TW_JS = json.dumps(_fx_tw)
    print(f"FX: {sum(1 for v in fx_raw if v)}/{len(fx_raw)} days present, "
          f"gaps on {[dates[i] for i,v in enumerate(fx_raw) if not v] or 'none'}")
else:
    print(f"FX: no '{FX_COL}' column in {prices_csv} — overlay omitted.")

# --- optional 4th arg: portfolio.json path → inject portfolio-value-over-time chart ---
portfolio_json_path = sys.argv[4] if len(sys.argv) > 4 else None
VALUE_CHART_CARD = ''
VALUE_CHART_SCRIPT = ''
OVERALL_TWR_JS = 'null'   # time-weighted-return series for the Overall perf line (set when portfolio.json is supplied)

_CARD = '''  <div class="card" style="margin-bottom:16px">
    <h2>Portfolio value over time</h2>
    <p class="cap">Market value in AUD of each holding and the whole book, as your position grew &mdash; units held each day &times; that day's close</p>
    <div class="perf-legend" id="valLegend"></div>
    <div class="perfwrap" id="valWrap">
      <svg id="valchart" width="100%" viewBox="0 0 900 340" role="img" aria-label="Portfolio value over time line chart" style="display:block"></svg>
      <div class="perf-tip" id="valTip"></div>
    </div>
    <p class="note" style="margin-top:10px">Each line steps up when you bought more of a holding, so this tracks the book <strong>growing with your contributions</strong>, not price alone. Value = units held on each ASX trading day &times; that day's close (AUD), reconstructed from your trade ledger (portfolio.json) and Hermes's daily prices. Lines start 3&nbsp;Jun&nbsp;2026, your first purchase; a same-day buy shows up once that day's close posts.</p>
  </div>

'''

_SCRIPT = '''<script>
(function(){
  const VORDER=%(order)s;
  const VCOLORS={IVV:'--s1',PMGOLD:'--s2',VGE:'--s3',VEQ:'--s4',VGS:'--s5'};
  const VTRADES=%(trades)s;
  const VPRICES=%(prices)s;
  const vcss=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const AUD0=n=>'$'+Math.round(n).toLocaleString('en-AU');
  const AUD2=n=>(n<0?'-':'')+'$'+Math.abs(n).toLocaleString('en-AU',{minimumFractionDigits:2,maximumFractionDigits:2});
  const firstD=VTRADES.reduce((m,t)=>t.d<m?t.d:m,VTRADES[0].d);
  const rows=VPRICES.filter(r=>r[0]>=firstD);
  const n=rows.length;
  const unitsAt=(tk,date)=>{let u=0;for(const t of VTRADES){if(t.t===tk&&t.d<=date)u+=t.u;}return u;};
  const series=VORDER.map(tk=>({tk,color:vcss(VCOLORS[tk]),vals:rows.map(r=>unitsAt(tk,r[0])*r[VORDER.indexOf(tk)+1])}));
  const overall={tk:'Overall',color:vcss('--ink'),tot:true,vals:rows.map((r,i)=>series.reduce((s,se)=>s+se.vals[i],0))};
  const all=[...series,overall];
  const mon=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  function draw(){
    const svg=document.getElementById('valchart'); if(!svg) return;
    const W=900,H=340,padL=60,padR=64,padT=16,padB=30;
    const plotW=W-padL-padR, plotH=H-padT-padB;
    let hi=0; all.forEach(s=>s.vals.forEach(v=>{if(v>hi)hi=v;}));
    hi=hi*1.08||1; const lo=0;
    const X=i=>padL+(n===1?0:i/(n-1)*plotW);
    const Y=v=>padT+(hi-v)/(hi-lo)*plotH;
    const gc=vcss('--grid'), axc=vcss('--axis'), mut=vcss('--muted');
    let g='';
    const steps=5;
    for(let k=0;k<=steps;k++){
      const v=lo+(hi-lo)*k/steps, y=Y(v);
      g+=`<line x1="${padL}" y1="${y.toFixed(1)}" x2="${W-padR}" y2="${y.toFixed(1)}" stroke="${k===0?axc:gc}" stroke-width="${k===0?1.4:1}"/>`;
      g+=`<text x="${padL-8}" y="${(y+3.5).toFixed(1)}" text-anchor="end" font-size="11" fill="${mut}">${AUD0(v)}</text>`;
    }
    const ticks=[0,Math.round((n-1)*0.25),Math.round((n-1)*0.5),Math.round((n-1)*0.75),n-1];
    [...new Set(ticks)].forEach(i=>{
      const d=rows[i][0].split('-'); const lab=parseInt(d[2],10)+' '+mon[+d[1]-1];
      g+=`<text x="${X(i).toFixed(1)}" y="${H-10}" text-anchor="middle" font-size="11" fill="${mut}">${lab}</text>`;
    });
    const path=s=>s.vals.map((v,i)=>`${i?'L':'M'}${X(i).toFixed(1)} ${Y(v).toFixed(1)}`).join(' ');
    series.forEach(s=>{ g+=`<path d="${path(s)}" fill="none" stroke="${s.color}" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round" opacity="0.95"/>`; });
    g+=`<path d="${path(overall)}" fill="none" stroke="${overall.color}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>`;
    all.forEach(s=>{ const v=s.vals[n-1],y=Y(v); g+=`<text x="${W-padR+6}" y="${(y+3.5).toFixed(1)}" font-size="11" font-weight="${s.tot?'700':'600'}" fill="${s.color}">${AUD0(v)}</text>`; });
    g+=`<line id="valCross" x1="0" y1="${padT}" x2="0" y2="${padT+plotH}" stroke="${axc}" stroke-width="1" opacity="0"/>`;
    all.forEach((s,idx)=>{ g+=`<circle id="vd${idx}" r="3.5" fill="${s.color}" stroke="${vcss('--surface')}" stroke-width="1.5" opacity="0"/>`; });
    g+=`<rect id="valHit" x="${padL}" y="${padT}" width="${plotW}" height="${plotH}" fill="transparent"/>`;
    svg.innerHTML=g;

    document.getElementById('valLegend').innerHTML=
      all.map(s=>`<div class="row ${s.tot?'tot':''}"><span class="ln" style="border-top-color:${s.color};${s.tot?'border-top-width:3px':''}"></span>${s.tk}</div>`).join('');

    const tip=document.getElementById('valTip'), cross=document.getElementById('valCross'), wrap=document.getElementById('valWrap');
    const dots=all.map((_,idx)=>document.getElementById('vd'+idx));
    function move(clientX){
      const rect=svg.getBoundingClientRect();
      const vx=(clientX-rect.left)/rect.width*W;
      let i=Math.round((vx-padL)/plotW*(n-1)); i=Math.max(0,Math.min(n-1,i));
      const xU=X(i);
      cross.setAttribute('x1',xU); cross.setAttribute('x2',xU); cross.setAttribute('opacity','1');
      all.forEach((s,idx)=>{ dots[idx].setAttribute('cx',xU); dots[idx].setAttribute('cy',Y(s.vals[i])); dots[idx].setAttribute('opacity','1'); });
      const d=rows[i][0].split('-'); const dlab=parseInt(d[2],10)+' '+mon[+d[1]-1]+' '+d[0];
      tip.innerHTML=`<div class="d">${dlab}</div>`+
        all.map(s=>`<div class="r"><span class="sw" style="background:${s.color}"></span><span class="nm">${s.tk}</span><span class="v" style="color:${s.tot?vcss('--ink'):'inherit'}">${AUD2(s.vals[i])}</span></div>`).join('');
      tip.style.opacity='1';
      const xpx=xU/W*rect.width;
      let left=xpx+14; if(left>wrap.clientWidth-150) left=xpx-tip.offsetWidth-14;
      tip.style.left=Math.max(0,left)+'px'; tip.style.top='6px';
    }
    svg.addEventListener('mousemove',e=>move(e.clientX));
    svg.addEventListener('mouseleave',()=>{tip.style.opacity='0';cross.setAttribute('opacity','0');dots.forEach(d=>d.setAttribute('opacity','0'));});
    svg.addEventListener('touchmove',e=>{if(e.touches[0])move(e.touches[0].clientX);},{passive:true});
  }
  draw();
  const tb=document.getElementById('themeBtn'); if(tb) tb.addEventListener('click',()=>setTimeout(draw,0));
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{ if(document.documentElement.getAttribute('data-theme')==='auto') draw(); });
})();
</script>
'''

if portfolio_json_path:
    try:
        pj = json.load(open(portfolio_json_path))
        vtrades = []
        for t in pj["trades"]:
            d = t["timestamp"][:10]
            u = t["units"] if t["type"].upper() == "BUY" else -t["units"]
            vtrades.append({"t": t["ticker"], "u": u, "d": d, "p": t["price"]})
        # VPRICES from already-parsed prices: [date, IVV, PMGOLD, VGE, VEQ]
        # (nulls preserved — no forward-fill; chart may show gaps on last row)
        first_trade_d = min(x["d"] for x in vtrades)
        vprices_raw = [[r[0]] + [v if v is not None else None for v in r[1:]] for r in prices]
        # sanity check
        last_date = vprices_raw[-1][0]
        def units_at(tk, date):
            return sum(x["u"] for x in vtrades if x["t"] == tk and x["d"] <= date)
        def running_cost_at(tk, date):
            # running cost basis: Σ (units × fill price) for lots settled on or before `date`.
            # Uses the real per-lot fill prices from portfolio.json (NOT trade-date closes).
            return sum(x["u"] * x["p"] for x in vtrades if x["t"] == tk and x["d"] <= date)
        print(f"Value chart: first trade {first_trade_d} | last price {last_date}")
        print(f"  units @ last date: { {tk: units_at(tk, last_date) for tk in ORDER} }")
        plot = [r for r in vprices_raw if r[0] >= first_trade_d]
        def overall_val(r):
            return sum(units_at(tk, r[0]) * r[i+1] for i, tk in enumerate(ORDER))
        ov = [overall_val(r) for r in plot]
        print(f"  overall: start ${ov[0]:.2f} ({plot[0][0]})  end ${ov[-1]:.2f} ({plot[-1][0]})  max ${max(ov):.2f}")
        # --- time-weighted return series for the Overall perf line (aligned 1:1 with `prices`) ---
        # Each day chains the market return of the units held going INTO that day (units_at(prev_date)),
        # marked from the previous close to that day's close. New purchases that day are excluded from
        # the day's return, so contribution timing does not distort it. Flat at 0 until first purchase.
        twr_series = []
        twr_cum = 1.0
        for _i in range(len(prices)):
            if _i == 0:
                twr_series.append(0.0)
                continue
            _row = prices[_i]
            _prow = prices[_i-1]
            _pdate = _prow[0]
            _v_start = 0.0
            _v_now = 0.0
            for _j, _tk in enumerate(ORDER):
                _u = units_at(_tk, _pdate)
                _pp = _prow[_j+1]
                _pn = _row[_j+1]
                if _pp is None or _pn is None or _u == 0:
                    continue
                _v_start += _u * _pp
                _v_now += _u * _pn
            if _v_start > 0:
                twr_cum *= (_v_now / _v_start)
            twr_series.append(round((twr_cum - 1) * 100, 4))
        OVERALL_TWR_JS = json.dumps(twr_series)
        print(f"  TWR overall: end {twr_series[-1]:.2f}%  (money-weighted total P/L% for reference in table)")

        # --- dollar-weighted Overall series for View 1 ---
        # At each date t: val = Σ units_held(t) × price(t); cost = Σ lot.units × lot.fill_price
        # over lots settled on or before t. DW = (val/cost − 1) × 100. This uses a RUNNING
        # cost basis (the lots actually held), not the final blended average entry projected
        # backwards — so early dates show the P/L he actually had at the time, and day one is
        # close/fill − 1 (a small non-zero), not forced to zero.
        # Null (not 0.0) before the first purchase, so the JS path skips those dates.
        dw_series = []
        for _i in range(len(prices)):
            _row = prices[_i]
            _row_date = _row[0]
            _val_sum = 0.0
            _cost_sum = 0.0
            for _j, _tk in enumerate(ORDER):
                _u = units_at(_tk, _row_date)
                _p = _row[_j+1]
                if _p is None or _u == 0:
                    continue
                _val_sum += _u * _p
                _cost_sum += running_cost_at(_tk, _row_date)
            if _cost_sum > 0:
                dw_series.append(round((_val_sum / _cost_sum - 1) * 100, 4))
            else:
                dw_series.append(None)
        DW_OVERALL_JS = json.dumps(dw_series)
        # Base the DW FX line on the same day DW_OVERALL starts. In this mode
        # each holding starts at its OWN first purchase (VGS has ~18 points
        # where IVV has ~70), so an FX line based at index 0 would span a
        # window none of them share and would appear to explain far more than
        # it does. Derived from the data, not hardcoded: holdings change.
        _dw_base = next((i for i, v in enumerate(dw_series) if v is not None), None)
        _fx_dw = _fx_pct(_dw_base, clip_before_base=True)
        if _fx_dw is not None:
            FX_DW_JS = json.dumps(_fx_dw)
            print(f"  FX DW baseline: index {_dw_base} ({dates[_dw_base]}) "
                  f"— aligned with DW Overall, not with individual holdings")
        _dw_last = next((v for v in reversed(dw_series) if v is not None), 0.0)
        print(f"  DW overall: end {_dw_last:.2f}%  (nulls before first purchase: {dw_series.count(None)})")

        # --- dollar-weighted per-holding series for View 1 ---
        # Each holding: price(t) / running_avg_cost(t) − 1, where running_avg_cost is the
        # fill-price-weighted cost of the lots actually held on date t. Null before the
        # ticker's first purchase (no line drawn) and null where the price is missing.
        dw_per_holding = {}
        for _j, _tk in enumerate(ORDER):
            _col = [r[_j+1] for r in prices]
            _first_d = min((x["d"] for x in vtrades if x["t"] == _tk), default=None)
            _series = []
            for _i in range(len(prices)):
                _date = prices[_i][0]
                _p = _col[_i]
                if _first_d is None or _date < _first_d:
                    _series.append(None)   # not owned yet — no line
                    continue
                if _p is None:
                    _series.append(None)   # price missing — gap
                    continue
                _u = units_at(_tk, _date)
                _c = running_cost_at(_tk, _date)
                if _u <= 0 or _c <= 0:
                    _series.append(None)
                else:
                    _series.append(round((_p / (_c / _u) - 1) * 100, 4))
            dw_per_holding[_tk] = _series
        DW_PER_HOLDING_JS = json.dumps(dw_per_holding)

        # --- time-weighted per-holding series for View 2 ---
        # Each holding: price(t) / price(series_start) − 1, shared baseline
        tw_per_holding_js = {}
        for _j, _tk in enumerate(ORDER):
            _prices_col = [r[_j+1] for r in prices]
            _baseline = next((p for p in _prices_col if p is not None), None)
            if _baseline is None or _baseline == 0:
                tw_per_holding_js[_tk] = [0.0] * len(prices)
            else:
                _series = []
                for _p in _prices_col:
                    if _p is None:
                        _series.append(None)  # gap
                    else:
                        _series.append(round((_p / _baseline - 1) * 100, 4))
                tw_per_holding_js[_tk] = _series
        TW_PER_HOLDING_JS = json.dumps(tw_per_holding_js)
        print(f"  TW per-holding baselines: { {tk: series[0] for tk, series in tw_per_holding_js.items()} }")

        # --- first-purchase-date index for each holding (for de-emphasised un-owned stretch in View 2) ---
        first_purchase_idx = {}
        for _j, _tk in enumerate(ORDER):
            _first_d = min(x["d"] for x in vtrades if x["t"] == _tk)
            # Find the first price row where date >= first purchase date
            _idx = 0
            for _idx in range(len(prices)):
                if prices[_idx][0] >= _first_d:
                    break
            first_purchase_idx[_tk] = _idx
        FIRST_PURCHASE_IDX_JS = json.dumps(first_purchase_idx)
        print(f"  First-purchase indices: {first_purchase_idx}")

        VALUE_CHART_CARD = _CARD
        VALUE_CHART_SCRIPT = _SCRIPT % {
            "order": json.dumps(ORDER),
            "trades": json.dumps(vtrades),
            "prices": json.dumps(vprices_raw),
        }
    except Exception as e:
        import traceback
        print(f"Portfolio value chart: could not parse portfolio.json — {e}. Omitting chart.")
        traceback.print_exc()

# --- emit JS arrays ---
hold_js='[\n'+',\n'.join(
    "  {tk:'%s', nm:'%s', cls:'%s', units:%s, entry:%s, price:%s, cvar:'%s'}"%(
        tk, META[tk]['nm'].replace("'","\\'"), META[tk]['cls'],
        (int(hold[tk]['units']) if hold[tk]['units']==int(hold[tk]['units']) else hold[tk]['units']),
        hold[tk]['entry'], hold[tk]['current'], META[tk]['cvar'])
    for tk in ORDER)+'\n]'
prices_js='[\n'+',\n'.join(json.dumps(r) for r in prices)+'\n]'

tpl=TEMPLATE
out=tpl.replace('__HOLDINGS__',hold_js).replace('__PRICES__',prices_js)
out=out.replace('__VALUE_CHART_CARD__', VALUE_CHART_CARD).replace('__VALUE_CHART_SCRIPT__', VALUE_CHART_SCRIPT)
out=out.replace('__OVERALL_TWR__', OVERALL_TWR_JS)
out=out.replace('__DW_OVERALL__', DW_OVERALL_JS if portfolio_json_path else 'null')
out=out.replace('__DW_PER_HOLDING__', DW_PER_HOLDING_JS if portfolio_json_path else 'null')
out=out.replace('__TW_PER_HOLDING__', TW_PER_HOLDING_JS if portfolio_json_path else 'null')
out=out.replace('__FIRST_PURCHASE_IDX__', FIRST_PURCHASE_IDX_JS if portfolio_json_path else 'null')
out=out.replace('__FX_TW__', FX_TW_JS)
out=out.replace('__FX_DW__', FX_DW_JS)
stamp = "%s/%s/%s" % (dates[-1][8:10], dates[-1][5:7], dates[-1][2:4])
out = out.replace('__STAMP__', stamp)
open(out_path,'w').write(out)

print("OK ->",out_path)
print("last close row:", prices[-1])
print("holdings current:", {tk:hold[tk]['current'] for tk in ORDER})
print("mapping:", mapping)
print("NOTES:", notes if notes else "none (no correction needed)")