import {score,rank,validate,normalise} from '../assets/index/core.js';
const dims=['a','b','c','d','e','f'].map(id=>({id,name:id}));
const country=(code,values)=>({code,name:code,region:'Sample',records:[{year:2024,scores:Object.fromEntries(dims.map((d,i)=>[d.id,values[i]]))}]});
const assert=(condition,message)=>{if(!condition)throw new Error(message);};
const rejects=(fn)=>{let threw=false;try{fn();}catch{threw=true;}assert(threw,'Expected invalid data to be rejected');};
Deno.test('overall requires all six dimensions; zero remains an observation',()=>{
 assert(score(country('A',[0,0,0,0,0,0]),2024,'overall',dims)===0,'Zero is valid');
 assert(score(country('A',[100,100,100,100,100,100]),2024,'overall',dims)===100,'Upper bound');
 assert(score(country('A',[10,20,30,40,50,60]),2024,'overall',dims)===35,'Equal-weight mean');
 assert(score(country('A',[10,20,null,40,50,60]),2024,'overall',dims)===null,'Missing must not become zero');
 assert(score(country('A',[10,20,30,40,50,60]),2023,'overall',dims)===null,'Missing year');
});
Deno.test('competition ranks preserve ties, skip missing values and use the full supplied sample',()=>{
 const a=country('A',[80,80,80,80,80,80]),b=country('B',[80,80,80,80,80,80]),c=country('C',[30,30,30,30,30,30]),missing=country('D',[null,0,0,0,0,0]),all=[a,b,c,missing];
 assert(rank(a,'overall',2024,all,dims)===1,'First tie');assert(rank(b,'overall',2024,all,dims)===1,'Second tie');assert(rank(c,'overall',2024,all,dims)===3,'Rank skips tied places');assert(rank(missing,'overall',2024,all,dims)===null,'Missing has no rank');
});
Deno.test('overall ranks follow the rounded displayed scores',()=>{
 const a=country('A',[50,50,50,50,50,50]),b=country('B',[50,50,50,50,50,50.2]);assert(rank(b,'overall',2024,[a,b],dims)===1,'Rounded tie');assert(rank(a,'overall',2024,[a,b],dims)===1,'Same displayed value shares rank');
});
Deno.test('validation rejects non-demo data, duplicate identifiers, invalid score types and bounds',()=>{
 const good=()=>({status:'synthetic-demo',dimensions:dims,years:[2024],countries:[country('A',[0,20,30,40,50,100])]});
 validate(good());const missing=good();missing.countries[0].records[0].scores.a=null;validate(missing);
 for(const value of [-1,101,'50',NaN,Infinity]){const d=good();d.countries[0].records[0].scores.a=value;rejects(()=>validate(d));}
 const prod=good();prod.status='official';rejects(()=>validate(prod));const duplicate=good();duplicate.countries.push(duplicate.countries[0]);rejects(()=>validate(duplicate));const years=good();years.countries[0].records.push(years.countries[0].records[0]);rejects(()=>validate(years));
});
Deno.test('country search accepts accent-free Türkiye',()=>{assert(normalise('Türkiye')===normalise('turkiye'),'Diacritics are ignored');});
Deno.test('the shipped fixture satisfies the demo contract',async()=>{
 const data=validate(JSON.parse(await Deno.readTextFile(new URL('../assets/index/demo-data.json',import.meta.url))));
 assert(data.countries.length===10,'Ten sample countries');assert(data.years.length===3,'Three sample years');
 for(const c of data.countries)for(const y of data.years)assert(score(c,y,'overall',data.dimensions)!=null,'All shipped sample records have an overall score');
});
