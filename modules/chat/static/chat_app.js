(function(){
"use strict";
const peer=window.LCU_PEER_ID;
if(!peer)return;

const body=document.getElementById("threadBody");
if(!body){return;}
const form=document.getElementById("chatForm");
const msg=document.getElementById("messageBox");
const fileInput=document.getElementById("attachmentInput");
const selected=document.getElementById("selectedFile");
const tools=document.getElementById("chatTools");
const emoji=document.getElementById("emojiBox");
const micBtn=document.getElementById("micBtn");
const recStatus=document.getElementById("recordStatus");
let lastId=0,pollBusy=false,sending=false,recorder=null,chunks=[],recordStream=null;

document.querySelectorAll("[data-msg-id]").forEach(x=>lastId=Math.max(lastId,parseInt(x.dataset.msgId||"0",10)));
body.scrollTop=body.scrollHeight;


function esc(s){return String(s||"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));}
function timeOnly(s){return (s&&s.length>=16)?s.slice(11,16):s||"";}

function renderMessage(m){
  if(document.querySelector(`[data-msg-id="${m.id}"]`))return;
  const mine=Number(m.sender_id)===Number(window.LCU_USER_ID);
  let media="";
  if(m.attachment_id){
    const url=`/chat/attachment/${m.attachment_id}`;
    if(m.attachment_kind==="audio"){
      media=`<div class="file"><audio class="audio" controls preload="metadata" src="${url}"></audio><div class="file-name">🎙 ${esc(m.attachment_name||"Voice message")}</div></div>`;
    }else if(m.attachment_kind==="image"){
      media=`<a href="${url}" target="_blank"><img class="image" src="${url}" alt="${esc(m.attachment_name)}"></a>`;
    }else{
      media=`<div class="file"><div class="file-row"><div class="file-icon">📄</div><div style="min-width:0"><div class="file-name">${esc(m.attachment_name||"Attachment")}</div><a href="${url}?download=1">Open / Download</a></div></div></div>`;
    }
  }
  let lead="";
  if(m.lead_id){
    lead=`<div class="lead"><b>🔒 CRM Client</b><br>${esc(m.lead_code)} • ${esc(m.client_name||"Client")}<br><small>${esc(m.lead_status)} • Interest ${m.interest_score||0}%</small><br><a href="/lead/${m.lead_id}">Open Client</a></div>`;
  }
  const row=document.createElement("div");
  row.className="row "+(mine?"mine":"theirs");
  row.dataset.msgId=m.id;
  row.innerHTML=`<div class="bubble">${m.message?`<div class="msgtext">${esc(m.message)}</div>`:""}${media}${lead}<div class="meta">${timeOnly(m.created_at)}${mine?`<span class="ticks">${m.read_at?"✓✓":"✓"}</span>`:""}</div></div>`;
  body.appendChild(row);
  lastId=Math.max(lastId,Number(m.id)||0);
}

async function refreshThread(forceBottom=false){
  if(pollBusy)return;
  pollBusy=true;
  const wasNearBottom=(body.scrollHeight-body.scrollTop-body.clientHeight)<120;
  try{
    const r=await fetch(`/v4/chat/thread?peer=${encodeURIComponent(peer)}&after=${lastId}`,{cache:"no-store",credentials:"same-origin"});
    if(r.ok){
      const j=await r.json();
      (j.messages||[]).forEach(renderMessage);
      lastId=Math.max(lastId,j.last_id||0);
      if(forceBottom||wasNearBottom)body.scrollTop=body.scrollHeight;
    }
  }catch(e){}
  pollBusy=false;
}
window.refreshThread=refreshThread;

async function sendForm(){
  if(sending)return;
  const hasText=msg.value.trim().length>0;
  const hasFile=fileInput.files&&fileInput.files.length>0;
  const lead=form.querySelector('[name="lead_id"]')?.value;
  if(!hasText&&!hasFile&&!lead)return;

  sending=true;
  document.getElementById("sendBtn").disabled=true;
  try{
    const fd=new FormData(form);
    const r=await fetch(form.action,{
      method:"POST",body:fd,credentials:"same-origin",
      headers:{"X-Requested-With":"XMLHttpRequest","Accept":"application/json"}
    });
    const j=await r.json().catch(()=>({ok:false,error:"Could not send"}));
    if(!r.ok||!j.ok)throw new Error(j.error||"Could not send message");
    msg.value="";
    fileInput.value="";
    selected.textContent="Nothing selected";
    tools.classList.remove("open");
    await refreshThread(true);
  }catch(e){
    alert(e.message||"Message could not be sent.");
  }finally{
    sending=false;
    document.getElementById("sendBtn").disabled=false;
    msg.focus();
  }
}

form.addEventListener("submit",e=>{e.preventDefault();sendForm();});
msg.addEventListener("keydown",e=>{
  if(e.key==="Enter"&&!e.shiftKey){
    e.preventDefault();sendForm();
  }
});
msg.addEventListener("input",()=>{
  msg.style.height="42px";
  msg.style.height=Math.min(120,msg.scrollHeight)+"px";
});

fileInput.addEventListener("change",()=>{
  if(fileInput.files&&fileInput.files[0]){
    selected.textContent=fileInput.files[0].name;
    tools.classList.add("open");
  }
});

window.toggleEmoji=function(){
  emoji.classList.toggle("open");
}
const emojis=["😀","😂","😊","😍","😘","😎","🥳","🤝","👍","🙏","❤️","🔥","✅","🎉","👏","💯","😄","😁","😉","😇","🤗","😅","😢","😡","🤔","🙌","💪","🌟","📌","⚡","🎯","💼"];
emoji.innerHTML=emojis.map(e=>`<button type="button">${e}</button>`).join("");
emoji.querySelectorAll("button").forEach(b=>b.onclick=()=>{
  msg.value+=b.textContent;emoji.classList.remove("open");msg.focus();
});

window.focusThreadSearch=function(){
  const q=prompt("Search word in this conversation:");
  if(!q)return;
  const needle=q.toLowerCase();
  const rows=[...document.querySelectorAll(".row")];
  const hit=rows.find(x=>x.textContent.toLowerCase().includes(needle));
  if(hit){hit.scrollIntoView({behavior:"smooth",block:"center"});hit.querySelector(".bubble").style.outline="2px solid #f3bd2f";setTimeout(()=>hit.querySelector(".bubble").style.outline="",1800);}
  else alert("No matching message currently loaded.");
}

window.toggleVoice=async function(){
  if(recorder&&recorder.state==="recording"){
    recorder.stop();
    return;
  }
  if(!navigator.mediaDevices||!window.MediaRecorder){
    alert("Voice recording is not supported by this browser. You can attach an audio file with the + button.");
    return;
  }
  try{
    recordStream=await navigator.mediaDevices.getUserMedia({audio:true});
    chunks=[];
    let preferred="";
    ["audio/webm;codecs=opus","audio/webm","audio/ogg"].some(t=>{
      if(MediaRecorder.isTypeSupported&&MediaRecorder.isTypeSupported(t)){preferred=t;return true}return false;
    });
    recorder=preferred?new MediaRecorder(recordStream,{mimeType:preferred}):new MediaRecorder(recordStream);
    recorder.ondataavailable=e=>{if(e.data&&e.data.size)chunks.push(e.data);};
    recorder.onstop=async ()=>{
      micBtn.classList.remove("recording");recStatus.classList.remove("show");
      if(recordStream)recordStream.getTracks().forEach(t=>t.stop());
      const mime=(recorder.mimeType||"audio/webm").split(";")[0];
      const ext=mime.includes("ogg")?"ogg":"webm";
      const blob=new Blob(chunks,{type:mime});
      if(blob.size<600){recorder=null;return;}
      const f=new File([blob],`Voice_${new Date().toISOString().replace(/[:.]/g,"-")}.${ext}`,{type:mime});
      const dt=new DataTransfer();dt.items.add(f);fileInput.files=dt.files;
      selected.textContent="🎙 "+f.name;
      tools.classList.add("open");
      recorder=null;
      await sendForm();
    };
    recorder.start();
    micBtn.classList.add("recording");recStatus.classList.add("show");
  }catch(e){
    alert("Microphone permission was not granted. Please allow microphone access or attach an audio file.");
  }
}

const search=document.getElementById("peopleSearch");
if(search)search.addEventListener("input",()=>{
  const q=search.value.trim().toLowerCase();
  document.querySelectorAll(".person").forEach(p=>p.style.display=p.dataset.name.includes(q)?"grid":"none");
});

setInterval(()=>refreshThread(false),2000);
window.addEventListener("focus",()=>refreshThread(false));
document.addEventListener("visibilitychange",()=>{if(!document.hidden)refreshThread(false);});
msg.focus();

function enforceDesktopLayout(){
  if(window.innerWidth>=921){
    const side=document.querySelector(".sidebar");
    const main=document.querySelector(".main");
    if(side){side.style.display="grid";}
    if(main){main.style.display="grid";}
  }
}
window.addEventListener("resize",enforceDesktopLayout);
enforceDesktopLayout();

})();
