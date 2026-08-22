(function(){
"use strict";

/*
  v4.7.1 — lightweight AM revert/status list
  No polling, no MutationObserver, no network requests.
  Runs once only on pages where a status dropdown is actually present.
*/
const STATUSES=[
  "Interested",
  "Not Interested",
  "Call Back",
  "Not Picked",
  "No Plan",
  "Budget Issue",
  "Not Connected",
  "Invalid No.",
  "No WhatsApp",
  "Enrolled",
  "Discussion",
  "Follow Up",
  "Payment After Visa",
  "Closed",
  "Office Visit",
  "Docs Received"
];

const ALIASES={
  "Follow-up":"Follow Up",
  "Follow up":"Follow Up",
  "Called":"Call Back",
  "Visit":"Office Visit",
  "Office Visit":"Office Visit",
  "Documents Pending":"Docs Received",
  "Docs Recived":"Docs Received",
  "Enroled":"Enrolled"
};

function normalize(v){
  v=(v||"").trim();
  return ALIASES[v]||v;
}

function rebuildSelect(sel){
  if(!sel || sel.dataset.v471StatusReady==="1") return;

  const raw=(sel.value||"").trim();
  const normalized=normalize(raw);
  const hasAll=[...sel.options].some(o=>o.value==="");

  const frag=document.createDocumentFragment();

  if(hasAll){
    const all=document.createElement("option");
    all.value="";
    all.textContent="All Status";
    frag.appendChild(all);
  }

  for(const status of STATUSES){
    const o=document.createElement("option");
    o.value=status;
    o.textContent=status;
    frag.appendChild(o);
  }

  // Keep any truly unknown historical value visible instead of losing data.
  if(normalized && !STATUSES.includes(normalized)){
    const legacy=document.createElement("option");
    legacy.value=raw;
    legacy.textContent=raw+" (Legacy)";
    frag.appendChild(legacy);
  }

  sel.replaceChildren(frag);

  if(normalized && STATUSES.includes(normalized)){
    sel.value=normalized;
  }else if(raw){
    sel.value=raw;
  }else if(hasAll){
    sel.value="";
  }

  sel.dataset.v471StatusReady="1";
}

function apply(){
  const selects=document.querySelectorAll('select[name="status"]');
  if(!selects.length) return;
  selects.forEach(rebuildSelect);
}

if(document.readyState==="loading"){
  document.addEventListener("DOMContentLoaded",apply,{once:true});
}else{
  apply();
}
})();
