(function(){
"use strict";

const STATUSES=[
"Interested","Not Interested","Call Back","Not Picked","No Plan","Budget Issue",
"Not Connected","Invalid No.","No WhatsApp","Enrolled","Discussion","Follow Up",
"Payment After Visa","Closed","Visit","Docs Received"
];

const ALIASES={
"Follow-up":"Follow Up","Follow up":"Follow Up","Office Visit":"Visit",
"Documents Pending":"Docs Received","Docs Recived":"Docs Received",
"Enroled":"Enrolled","Called":"Call Back"
};

function normalize(v){
  v=(v||"").trim();
  return ALIASES[v]||v;
}

function rebuildSelect(sel){
  if(!sel || sel.dataset.v462StatusReady==="1") return;

  const raw=(sel.value||"").trim();
  const oldValue=normalize(raw);
  const hasAll=[...sel.options].some(o=>o.value==="");

  const frag=document.createDocumentFragment();
  if(hasAll){
    const o=document.createElement("option");
    o.value=""; o.textContent="All Status";
    frag.appendChild(o);
  }

  for(const s of STATUSES){
    const o=document.createElement("option");
    o.value=s; o.textContent=s;
    frag.appendChild(o);
  }

  if(oldValue && !STATUSES.includes(oldValue)){
    const o=document.createElement("option");
    o.value=raw; o.textContent=raw+" (Legacy)";
    frag.appendChild(o);
  }

  sel.replaceChildren(frag);
  if(oldValue && STATUSES.includes(oldValue)) sel.value=oldValue;
  else if(raw) sel.value=raw;
  else if(hasAll) sel.value="";

  sel.dataset.v462StatusReady="1";
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
