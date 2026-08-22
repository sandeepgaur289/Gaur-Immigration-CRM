(function(){
"use strict";

function clean(s){return String(s||"").replace(/\s+/g," ").trim();}
function title(){
  const el=document.querySelector("h1.title,main h1,main h2,.title");
  return clean(el?el.textContent:document.title)||"THE GAUR CRM Report";
}
function scope(){
  const text=(document.body&&document.body.innerText)||"";
  const sc=/Smart Choice|SCIC/i.test(text), ww=/White Wave|WWIC/i.test(text);
  if(sc&&!ww)return "Smart Choice";
  if(ww&&!sc)return "White Wave";
  return "Both Companies";
}
function toast(msg){
  let d=document.getElementById("gaurReportToolToast");
  if(!d){
    d=document.createElement("div");
    d.id="gaurReportToolToast";
    d.style.cssText="position:fixed;right:20px;top:20px;z-index:2147483647;background:#0b5d4f;color:#fff;border:2px solid #e6b73f;border-radius:10px;padding:10px 14px;font:700 13px Arial;box-shadow:0 8px 28px rgba(0,0,0,.35)";
    document.body.appendChild(d);
  }
  d.textContent=msg;d.style.display="block";
  clearTimeout(d._t);d._t=setTimeout(()=>d.style.display="none",1800);
}
function metrics(){
  const out=[],seen=new Set();
  document.querySelectorAll("main .card,main [class*='stat'],main [class*='metric'],main [class*='dashboard'],main [class*='today'],main [class*='kpi']").forEach(el=>{
    if(el.offsetParent===null)return;
    const txt=clean(el.innerText);
    if(!txt||txt.length>220)return;
    const vals=txt.match(/₹\s?[\d,]+(?:\.\d+)?|[\d,]+(?:\.\d+)?%/g);
    if(!vals||!vals.length)return;
    const value=vals[0],label=clean(txt.replace(value,""));
    if(!label||label.length>100)return;
    const k=label+"|"+value;
    if(!seen.has(k)){seen.add(k);out.push({label,value});}
  });
  return out.slice(0,300);
}
function tables(){
  const out=[];
  document.querySelectorAll("main table,table").forEach((t,i)=>{
    if(t.offsetParent===null)return;
    const rows=[];
    t.querySelectorAll("tr").forEach(tr=>{
      const r=[...tr.querySelectorAll("th,td")].map(x=>clean(x.innerText));
      if(r.length)rows.push(r);
    });
    if(rows.length)out.push({name:"Table "+(i+1),rows});
  });
  return out;
}
function shareWhatsApp(ev){
  if(ev){ev.preventDefault();ev.stopImmediatePropagation();}
  toast("Opening WhatsApp…");
  let msg="THE GAUR CRM\n"+title()+"\nScope: "+scope();
  const m=metrics().slice(0,8);
  if(m.length){
    msg+="\n\n";
    m.forEach(x=>msg+=x.label+": "+x.value+"\n");
  }
  msg+="\nOpen Report: "+location.href;
  // Same-tab navigation cannot be blocked by popup blockers.
  location.href="https://wa.me/?text="+encodeURIComponent(msg);
  return false;
}
function printReport(ev){
  if(ev){ev.preventDefault();ev.stopImmediatePropagation();}
  toast("Opening Print / Save PDF…");
  setTimeout(()=>window.print(),80);
  return false;
}
async function downloadExcel(ev,btn){
  if(ev){ev.preventDefault();ev.stopImmediatePropagation();}
  btn=btn||document.getElementById("safeExcelBtn");
  const old=btn?btn.textContent:"";
  if(btn){btn.disabled=true;btn.textContent="Preparing Excel…";}
  toast("Preparing Excel…");
  try{
    const r=await fetch("/v4/report-tools/excel",{
      method:"POST",credentials:"same-origin",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({title:title(),url:location.href,metrics:metrics(),tables:tables()})
    });
    if(!r.ok){
      let e="Excel export failed.";
      try{const j=await r.json();e=j.error||e;}catch(_){}
      throw new Error(e);
    }
    const blob=await r.blob();
    let filename="CRM_Report.xlsx";
    const cd=r.headers.get("Content-Disposition")||"";
    const m=cd.match(/filename\*?=(?:UTF-8''|")?([^";]+)/i);
    if(m)filename=decodeURIComponent(m[1].replace(/"/g,""));
    const url=URL.createObjectURL(blob);
    const a=document.createElement("a");
    a.href=url;a.download=filename;a.style.display="none";
    document.body.appendChild(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),2500);
    toast("Excel downloaded.");
  }catch(err){
    alert(err.message||"Excel download could not start.");
  }finally{
    if(btn){btn.disabled=false;btn.textContent=old;}
  }
  return false;
}

window.GaurReportTools={shareWhatsApp,printReport,downloadExcel};

// Capture-level delegation defeats old/broken bubble listeners and also works if the toolbar is re-rendered later.
document.addEventListener("click",function(e){
  const el=e.target&&e.target.closest?e.target.closest("#safeWhatsAppBtn,#safePrintBtn,#safeExcelBtn"):null;
  if(!el)return;
  e.preventDefault();
  e.stopImmediatePropagation();
  if(el.id==="safeWhatsAppBtn")shareWhatsApp(e);
  else if(el.id==="safePrintBtn")printReport(e);
  else if(el.id==="safeExcelBtn")downloadExcel(e,el);
},true);

})();
