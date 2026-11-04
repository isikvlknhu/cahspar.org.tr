import {normalise, score as scoreFor, rank as rankFor, validate} from './core.js';
/* Synthetic fixtures only; production results require an approved methodology. */
(() => {
'use strict';
const root=document.getElementById('cahspar-explorer');
if(!root)return;
const $=id=>root.querySelector(`#ci-${id}`);
const state={year:null,region:'',query:'',view:'score',sort:'overall',descending:true,selected:new Set(),profile:'TUR'};
let data,dimensions;
const format=v=>v==null?'—':v.toFixed(1);
const score=(c,year,key)=>scoreFor(c,year,key,dimensions);
const rank=(c,key,year=state.year)=>rankFor(c,key,year,data.countries,dimensions);
const visible=()=>data.countries.filter(c=>(!state.region||c.region===state.region)&&(normalise(c.name).includes(normalise(state.query))||normalise(c.code).includes(normalise(state.query)))).sort((a,b)=>{
 if(state.sort==='name')return(state.descending?-1:1)*a.name.localeCompare(b.name,'en');
 const av=score(a,state.year,state.sort),bv=score(b,state.year,state.sort);
 if(av==null)return bv==null?a.name.localeCompare(b.name):1;
 if(bv==null)return -1;
 return(state.descending?bv-av:av-bv)||a.name.localeCompare(b.name,'en');
});
const node=(tag,text,cls)=>{const e=document.createElement(tag);if(text!=null)e.textContent=text;if(cls)e.className=cls;return e;};
function renderHead(){
 const row=node('tr');row.append(node('th','Compare'),node('th','Rank'));
 [{id:'name',name:'Country'},{id:'overall',name:'Overall'},...dimensions].forEach(d=>{
  const th=node('th'),active=state.sort===d.id;th.setAttribute('aria-sort',active?(state.descending?'descending':'ascending'):'none');
  const b=node('button',`${d.name} ${active?(state.descending?'↓':'↑'):'↕'}`);b.type='button';b.dataset.sort=d.id;
  b.setAttribute('aria-label',`Sort by ${d.name}${active?`, currently ${state.descending?'descending':'ascending'}`:''}`);th.append(b);row.append(th);
 });
 [...row.children].forEach(th=>th.scope='col');$('head').replaceChildren(row);
}
function renderRows(){
 const rows=visible(),body=document.createDocumentFragment();
 $('scale').textContent=state.view==='rank'?'Ranks: 1 is best · Full sample · Demo only':'Scores: 0–100 · Higher is better · Demo only';
 $('count').textContent=`${rows.length} of ${data.countries.length} sample countries · ${state.year} · Synthetic data`;
 rows.forEach(c=>{
  const row=node('tr');row.dataset.country=c.code;
  const checkCell=node('td'),check=node('input');check.type='checkbox';check.dataset.compare=c.code;check.checked=state.selected.has(c.code);check.disabled=state.selected.size>=3&&!check.checked;
  check.setAttribute('aria-label',`Compare ${c.name}`);check.setAttribute('aria-describedby','ci-compare-help');checkCell.append(check);
  const nameCell=node('td'),b=node('button',c.name,'ci-country');b.type='button';b.dataset.profile=c.code;b.setAttribute('aria-label',`View ${c.name} demonstration profile`);nameCell.append(b);
  row.append(checkCell,node('td',rank(c,'overall')??'—'),nameCell);
  ['overall',...dimensions.map(d=>d.id)].forEach(key=>{
   const td=node('td'),v=score(c,state.year,key),span=node('span',state.view==='rank'?String(rank(c,key)??'—'):format(v),'ci-score');
   if(v!=null)span.classList.add(v>=75?'ci-score-high':v>=55?'ci-score-mid':'ci-score-low');td.append(span);row.append(td);
  });body.append(row);
 });
 if(!rows.length){const row=node('tr'),cell=node('td','No countries match these filters. Clear the search or reset the filters.','ci-empty');cell.colSpan=10;row.append(cell);body.append(row);}
 $('body').replaceChildren(body);
}
function renderComparison(){
 const countries=data.countries.filter(c=>state.selected.has(c.code));
 $('compare-help').textContent=countries.length?`${countries.length} of 3 selected · ${state.year} · Synthetic scores. Selection is kept when filters change.`:'Select up to three countries in the table.';
 $('clear').disabled=!countries.length;$('comparison').replaceChildren();if(!countries.length)return;
 const table=node('table'),head=node('thead'),header=node('tr');table.append(node('caption',`Demonstration comparison · ${state.year} · Synthetic scores (0–100)`));header.append(node('th','Dimension'));
 countries.forEach(c=>header.append(node('th',c.name)));[...header.children].forEach(th=>th.scope='col');head.append(header);table.append(head);
 const body=node('tbody');[{id:'overall',name:'Overall'},...dimensions].forEach(d=>{const tr=node('tr'),th=node('th',d.name);th.scope='row';tr.append(th);countries.forEach(c=>tr.append(node('td',format(score(c,state.year,d.id)))));body.append(tr);});table.append(body);$('comparison').append(table);
}
function renderProfile(){
 const c=data.countries.find(c=>c.code===state.profile);if(!c)return;
 const section=$('profile');section.replaceChildren();
 const heading=node('div',null,'ci-profile-heading'),title=node('h3',`${c.name} / country profile`);title.id='ci-profile-title';heading.append(title,node('p',`SYNTHETIC DATA · ${state.year} · Overall ${format(score(c,state.year,'overall'))}/100`));section.append(heading);
 const grid=node('div',null,'ci-profile-grid'),bars=node('div',null,'ci-bars');
 dimensions.forEach(d=>{const item=node('div'),label=node('div',null,'ci-bar-label'),v=score(c,state.year,d.id);label.append(node('span',d.name),node('strong',format(v)));const track=node('div',null,'ci-bar-track'),fill=node('div',null,'ci-bar-fill');track.setAttribute('aria-hidden','true');fill.style.width=`${v??0}%`;track.append(fill);item.append(label,track);bars.append(item);});
 const trend=node('div',null,'ci-trend');trend.append(node('p','Overall score over sample years · fixed 0–100 scale'));
 const ns='http://www.w3.org/2000/svg',svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox','0 0 420 200');svg.setAttribute('role','img');svg.setAttribute('aria-label',`Synthetic overall trend for ${c.name}: ${data.years.map(y=>`${y}: ${format(score(c,y,'overall'))}`).join('; ')}`);
 const draw=(tag,attrs,text)=>{const e=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));if(text!=null)e.textContent=text;svg.append(e);return e;};
 [0,50,100].forEach(v=>{const y=160-v*1.3;draw('line',{x1:40,y1:y,x2:390,y2:y,stroke:'#cbd9d3'});draw('text',{x:6,y:y+4,fill:'#63717d','font-size':11},v);});
 const points=data.years.map((y,i)=>({year:y,value:score(c,y,'overall'),x:60+i*(310/Math.max(1,data.years.length-1))}));
 // Missing observations break the line rather than suggesting a measured trend.
 points.forEach((p,i)=>{const prev=points[i-1];if(prev?.value!=null&&p.value!=null)draw('line',{x1:prev.x,y1:160-prev.value*1.3,x2:p.x,y2:160-p.value*1.3,stroke:'#316b61','stroke-width':3});});
 points.forEach(p=>{draw('text',{x:p.x,y:187,'text-anchor':'middle',fill:'#123b59','font-size':11},p.year);if(p.value==null)return;const y=160-p.value*1.3;draw('circle',{cx:p.x,cy:y,r:4,fill:'#316b61'});draw('text',{x:p.x,y:y-12,'text-anchor':'middle',fill:'#123b59','font-size':12},format(p.value));});
 trend.append(svg);grid.append(bars,trend);section.append(grid,node('small','Illustrative values only. These scores and trends do not describe actual national performance.'));
}
function render(){renderHead();renderRows();renderComparison();renderProfile();}
function download(){
 const headers=['dataset_status','sample_year','country_code','country','region','overall_rank','overall_score',...dimensions.map(d=>`${d.id}_score`)];
 const rows=visible().map(c=>['SYNTHETIC DEMO - NOT OFFICIAL',state.year,c.code,c.name,c.region,rank(c,'overall'),score(c,state.year,'overall'),...dimensions.map(d=>score(c,state.year,d.id))]);
 const csv=[headers,...rows].map(row=>row.map(v=>`"${String(v??'').replace(/"/g,'""')}"`).join(',')).join('\r\n');
 const url=URL.createObjectURL(new Blob(['\uFEFF'+csv],{type:'text/csv;charset=utf-8'})),a=node('a');a.href=url;a.download=`cahspar-SYNTHETIC-DEMO-${state.year}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
async function start(){
 try{
  const response=await fetch(new URL('assets/index/demo-data.json',document.baseURI));if(!response.ok)throw new Error(`HTTP ${response.status}`);
  data=validate(await response.json());dimensions=data.dimensions;data.years.sort((a,b)=>a-b);state.year=data.years.at(-1);if(!data.countries.some(c=>c.code===state.profile))state.profile=data.countries[0].code;
  [...new Set(data.countries.map(c=>c.region))].sort().forEach(r=>{const o=node('option',r);o.value=r;$('region').append(o);});[...data.years].reverse().forEach(y=>{const o=node('option',y);o.value=y;$('year').append(o);});
  const table=node('table');table.id='ci-table';table.append(node('caption','Synthetic demonstration rankings. Select a country name for its profile, or up to three checkboxes to compare countries. Column buttons sort the table.','ci-sr'));const head=node('thead'),body=node('tbody');head.id='ci-head';body.id='ci-body';table.append(head,body);$('table-host').append(table);
  $('search').addEventListener('input',e=>{state.query=e.target.value.trim();renderRows();});$('region').addEventListener('change',e=>{state.region=e.target.value;renderRows();});$('year').addEventListener('change',e=>{state.year=Number(e.target.value);render();});
  root.querySelectorAll('[name=ci-view]').forEach(r=>r.addEventListener('change',e=>{state.view=e.target.value;renderRows();}));
  $('head').addEventListener('click',e=>{const b=e.target.closest('[data-sort]');if(!b)return;state.descending=state.sort===b.dataset.sort?!state.descending:b.dataset.sort!=='name';state.sort=b.dataset.sort;renderHead();renderRows();root.querySelector(`[data-sort="${state.sort}"]`).focus();});
  $('body').addEventListener('change',e=>{const code=e.target.dataset.compare;if(!code)return;if(e.target.checked&&state.selected.size<3)state.selected.add(code);else state.selected.delete(code);renderRows();renderComparison();root.querySelector(`[data-compare="${code}"]`)?.focus();});
  $('body').addEventListener('click',e=>{const b=e.target.closest('[data-profile]');if(!b)return;state.profile=b.dataset.profile;renderProfile();const t=$('profile-title');t.tabIndex=-1;t.focus({preventScroll:true});$('profile').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});});
  $('clear').addEventListener('click',()=>{state.selected.clear();renderRows();renderComparison();});
  $('reset').addEventListener('click',()=>{state.region='';state.query='';state.year=data.years.at(-1);state.view='score';state.sort='overall';state.descending=true;$('search').value='';$('region').value='';$('year').value=state.year;root.querySelector('[name=ci-view][value=score]').checked=true;render();});
  $('download').addEventListener('click',download);$('download').disabled=false;$('status').textContent='';$('app').hidden=false;render();
 }catch(error){$('status').className='ci-error';$('status').replaceChildren(node('p','The demonstration could not be loaded. The framework and methodology below are still available.'));const retry=node('button','Try again','ci-button');retry.type='button';retry.addEventListener('click',()=>location.reload());$('status').append(retry);console.error('ÇAHSPAR Index failed to load:',error);}
}
start();
})();
