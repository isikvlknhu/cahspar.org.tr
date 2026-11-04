// Calculation rules for the synthetic interface demonstration only.
export const normalise=v=>v.toLocaleLowerCase('en-GB').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
export const score=(c,year,key,dimensions)=>{
 const scores=c.records.find(r=>r.year===year)?.scores;
 if(!scores)return null;
 if(key!=='overall')return scores[key]??null;
 const values=dimensions.map(d=>scores[d.id]);
 return values.every(Number.isFinite)?Math.round(values.reduce((a,b)=>a+b,0)/values.length*10)/10:null;
};
export const rank=(c,key,year,countries,dimensions)=>{
 const v=score(c,year,key,dimensions);
 return v==null?null:1+countries.filter(other=>score(other,year,key,dimensions)!=null&&score(other,year,key,dimensions)>v).length;
};
export function validate(input){
 if(input.status!=='synthetic-demo'||!Array.isArray(input.dimensions)||input.dimensions.length!==6||!Array.isArray(input.years)||!input.years.length||!Array.isArray(input.countries)||!input.countries.length)throw new Error('Invalid demonstration dataset');
 const ids=input.dimensions.map(d=>d.id);
 if(new Set(ids).size!==6||input.dimensions.some(d=>typeof d.id!=='string'||typeof d.name!=='string')||input.years.some(y=>!Number.isInteger(y))||new Set(input.years).size!==input.years.length)throw new Error('Invalid dimensions or years');
 const codes=new Set();input.countries.forEach(c=>{
  if(typeof c.code!=='string'||codes.has(c.code)||typeof c.name!=='string'||typeof c.region!=='string'||!Array.isArray(c.records))throw new Error('Invalid country');codes.add(c.code);
  const years=new Set();c.records.forEach(r=>{if(!input.years.includes(r.year)||years.has(r.year)||!r.scores)throw new Error('Invalid country year');years.add(r.year);ids.forEach(id=>{const v=r.scores[id];if(v!=null&&(!Number.isFinite(v)||v<0||v>100))throw new Error('Invalid score');});});
 });return input;
}
