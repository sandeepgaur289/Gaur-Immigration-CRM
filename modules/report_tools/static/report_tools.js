(function(){
"use strict";

function clean(s){return String(s||"").replace(/\s+/g," ").trim();}
function pageTitle(){
  const el=document.querySelector("h1.title, main h1, main h2, .title");
  return clean(el?el.textContent:document.title)||"THE GAUR CRM Report";
}
function reportScope(){
  const t=document.body.innerText||"";
  if(/White Wave General Manager|WWIC/i.test(t)&&!/Smart Choice General Manager/i.test(t))return "White Wave";
  if(/Smart Choice General Manager|SCIC/i.test(t)&&!/White Wave General Manager/i.test(t))return "Smart Choice";
  return "Both Companies";
}
function collectMetrics(){
  const out=[], seen=new Set();
  const selectors=[
    ".identity-stat",".stat",".metric",".summary-card",".dashboard-card",
    ".today-stat",".today-metric",".kpi",".perf-box",
    "[class*='stat-card']","[class*='metric-card']"
  ];
  document.querySelectorAll(selectors.join(",")).forEach(el=>{
    if(el.offsetParent===null)return;
    const txt=clean(el.innerText);
    if(!txt||txt.length>180)return;
    let label="",value="";
    const b=el.querySelector("b,strong,.value,[class*='value']");
    if(b){
      value=clean(b.textContent);
      label=clean(txt.replace(value,""));
    }else{
      const lines=txt.split(/\n+/).map(clean).filter(Boolean);
      if(lines.length>=2){label=lines[0];value=lines.slice(1).join(" ");}
    }
    if(!label||!value)return;
    const key=label+"|"+value;
    if(seen.has(key))return;
    seen.add(key);out.push({label,value});
  });

  // Dashboard cards in this CRM often do not use generic stat class names.
  document.querySelectorAll("main div").forEach(el=>{
    if(out.length>250||el.offsetParent===null)return;
    if(el.children.length>8)return;
    const txt=clean(el.innerText);
    if(!txt||txt.length>100)return;
    const nums=txt.match(/₹?[\d,]+(?:\.\d+)?%?/g);
    if(!nums||nums.length!==1)return;
    const value=nums[0];
    const label=clean(txt.replace(value,""));
    if(label.length<3||label.length>65)return;
    const key=label+"|"+value;
    if(!seen.has(key)){seen.add(key);out.push({label,value});}
  });
  return out.slice(0,300);
}
function collectTables(){
  const tables=[];
  document.querySelectorAll("main table, table").forEach((t,i)=>{
    if(t.offsetParent===null)return;
    const rows=[];
    t.querySelectorAll("tr").forEach(tr=>{
      const cells=[...tr.querySelectorAll("th,td")].map(td=>clean(td.innerText));
      if(cells.length)rows.push(cells);
    });
    if(!rows.length)return;
    let name="";
    const cap=t.querySelector("caption");
    if(cap)name=clean(cap.textContent);
    if(!name){
      let prev=t.previousElementSibling;
      for(let n=0;prev&&n<4;n++,prev=prev.previousElementSibling){
        if(/^H[1-6]$/.test(prev.tagName)){name=clean(prev.textContent);break;}
      }
    }
    tables.push({name:name||("Table "+(i+1)),rows});
  });
  return tables;
}
function shareWhatsApp(){
  const metrics=collectMetrics().slice(0,10);
  let text="THE GAUR CRM\n"+pageTitle()+"\nScope: "+reportScope();
  if(metrics.length){
    text+="\n\n";
    metrics.forEach(x=>text+=x.label+": "+x.value+"\n");
  }
  text+="\nOpen Report: "+location.href;
  const a=document.createElement("a");
  a.href="https://wa.me/?text="+encodeURIComponent(text);
  a.target="_blank";a.rel="noopener";
  document.body.appendChild(a);a.click();a.remove();
}
function printReport(){
  document.documentElement.classList.add("v45-printing");
  setTimeout(()=>{
    window.print();
    setTimeout(()=>document.documentElement.classList.remove("v45-printing"),500);
  },50);
}
async function downloadExcel(btn){
  const old=btn.textContent;
  btn.disabled=true;btn.textContent="Preparing Excel…";
  try{
    const payload={
      title:pageTitle(),
      url:location.href,
      metrics:collectMetrics(),
      tables:collectTables()
    };
    const r=await fetch("/v4/report-tools/excel",{
      method:"POST",credentials:"same-origin",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(payload)
    });
    if(!r.ok){
      let msg="Excel export failed.";
      try{const j=await r.json();msg=j.error||msg;}catch(e){}
      throw new Error(msg);
    }
    const blob=await r.blob();
    const cd=r.headers.get("Content-Disposition")||"";
    let filename="CRM_Report.xlsx";
    const m=cd.match(/filename="?([^"]+)"?/i);
    if(m)filename=m[1];
    const url=URL.createObjectURL(blob);
    const a=document.createElement("a");
    a.href=url;a.download=filename;
    document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1500);
  }catch(e){
    alert(e.message||"Excel download could not start.");
  }finally{
    btn.disabled=false;btn.textContent=old;
  }
}
function bind(){
  const wa=document.getElementById("safeWhatsAppBtn");
  const pr=document.getElementById("safePrintBtn");
  const ex=document.getElementById("safeExcelBtn");

  // Capture phase + stopImmediatePropagation prevents broken legacy handlers from also firing.
  if(wa&&!wa.dataset.v45){
    wa.dataset.v45="1";
    wa.addEventListener("click",e=>{e.preventDefault();e.stopImmediatePropagation();shareWhatsApp();},true);
  }
  if(pr&&!pr.dataset.v45){
    pr.dataset.v45="1";
    pr.addEventListener("click",e=>{e.preventDefault();e.stopImmediatePropagation();printReport();},true);
  }
  if(ex&&!ex.dataset.v45){
    ex.dataset.v45="1";
    ex.addEventListener("click",e=>{e.preventDefault();e.stopImmediatePropagation();downloadExcel(ex);},true);
  }
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",bind);
else bind();
setTimeout(bind,600);
})();
