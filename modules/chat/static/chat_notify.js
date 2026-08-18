(function(){
"use strict";
const KEY_ENABLED="gaurChatAlertsEnabled";
const KEY_LAST="gaurChatLastMessageId";
const POLL_MS=5000;
let audioCtx=null, polling=false, baselineDone=false;

function enabled(){ return localStorage.getItem(KEY_ENABLED)==="1"; }
function setEnabled(v){ localStorage.setItem(KEY_ENABLED,v?"1":"0"); }

function unlockAudio(){
  try{
    const AC=window.AudioContext||window.webkitAudioContext;
    if(!AC) return false;
    if(!audioCtx) audioCtx=new AC();
    if(audioCtx.state==="suspended") audioCtx.resume();
    return true;
  }catch(e){ return false; }
}

function chime(){
  try{
    if(!enabled()) return;
    if(!unlockAudio()) return;
    const t=audioCtx.currentTime;
    [880,1175].forEach((freq,i)=>{
      const o=audioCtx.createOscillator();
      const g=audioCtx.createGain();
      o.type="sine"; o.frequency.value=freq;
      g.gain.setValueAtTime(0.0001,t+i*0.12);
      g.gain.exponentialRampToValueAtTime(0.18,t+i*0.12+0.02);
      g.gain.exponentialRampToValueAtTime(0.0001,t+i*0.12+0.22);
      o.connect(g); g.connect(audioCtx.destination);
      o.start(t+i*0.12); o.stop(t+i*0.12+0.24);
    });
  }catch(e){}
}

function ensureStyles(){
  if(document.getElementById("v42-chat-alert-style")) return;
  const s=document.createElement("style");
  s.id="v42-chat-alert-style";
  s.textContent=`
  #v42AlertEnable{position:fixed;right:18px;bottom:94px;z-index:2147483000;background:#075e54;border:2px solid #25d366;color:#fff;border-radius:16px;padding:12px 14px;box-shadow:0 10px 35px rgba(0,0,0,.38);font-family:Arial,sans-serif;max-width:310px}
  #v42AlertEnable b{display:block;color:#ffd45f;margin-bottom:4px}
  #v42AlertEnable button{margin-top:8px;background:#25d366;color:#062b20;border:0;border-radius:9px;padding:8px 12px;font-weight:800;cursor:pointer}
  #v42ToastWrap{position:fixed;right:18px;top:18px;z-index:2147483001;width:min(370px,calc(100vw - 36px));font-family:Arial,sans-serif}
  .v42toast{display:flex;gap:10px;align-items:flex-start;background:#08213a;border:2px solid #25d366;border-radius:14px;padding:11px;margin-bottom:8px;color:#fff;box-shadow:0 12px 34px rgba(0,0,0,.45);animation:v42in .2s ease}
  .v42toast img,.v42avatar{width:44px;height:44px;border-radius:50%;object-fit:cover;border:2px solid #25d366;flex:0 0 44px}
  .v42avatar{display:flex;align-items:center;justify-content:center;background:#075e54;font-weight:900}
  .v42toast .body{min-width:0;flex:1}.v42toast .name{font-weight:900;color:#ffd45f}.v42toast .msg{font-size:13px;margin-top:3px;line-height:1.32;overflow:hidden;text-overflow:ellipsis}
  .v42toast a{display:inline-block;margin-top:7px;background:#25d366;color:#052d21;padding:6px 10px;border-radius:8px;text-decoration:none;font-weight:800;font-size:12px}
  .v42toast .x{background:transparent;border:0;color:#fff;font-size:18px;cursor:pointer;padding:0}
  .v42-unread-badge{position:fixed;right:18px;bottom:18px;z-index:2147482999;background:#e53935;color:#fff;border-radius:999px;min-width:25px;height:25px;padding:0 7px;display:none;align-items:center;justify-content:center;font:bold 12px Arial;box-shadow:0 4px 12px rgba(0,0,0,.35)}
  @keyframes v42in{from{transform:translateY(-10px);opacity:0}to{transform:translateY(0);opacity:1}}
  @media(max-width:600px){#v42ToastWrap{top:8px;right:8px;width:calc(100vw - 16px)}#v42AlertEnable{right:10px;left:10px;bottom:86px;max-width:none}}
  `;
  document.head.appendChild(s);
}

async function askPermission(){
  unlockAudio();
  setEnabled(true);
  if("Notification" in window && Notification.permission==="default"){
    try{ await Notification.requestPermission(); }catch(e){}
  }
  const box=document.getElementById("v42AlertEnable");
  if(box) box.remove();
  chime();
}

function enablePrompt(){
  if(enabled()) return;
  const d=document.createElement("div");
  d.id="v42AlertEnable";
  d.innerHTML="<b>🔔 Chat Alerts</b><span>WhatsApp-style sound + popup for new CRM messages.</span><br><button type='button'>Enable Chat Alerts</button>";
  d.querySelector("button").addEventListener("click",askPermission);
  document.body.appendChild(d);
}

function toast(m){
  let wrap=document.getElementById("v42ToastWrap");
  if(!wrap){ wrap=document.createElement("div");wrap.id="v42ToastWrap";document.body.appendChild(wrap); }
  const d=document.createElement("div");d.className="v42toast";
  const avatar=m.photo_url?`<img src="${m.photo_url}" alt="">`:`<div class="v42avatar">${(m.sender_name||"?").charAt(0).toUpperCase()}</div>`;
  const safeName=(m.sender_name||"Team Member").replace(/[<>&"]/g,"");
  const safeMsg=(m.message||"New message").replace(/[<>&]/g,c=>({"<":"&lt;",">":"&gt;","&":"&amp;"}[c]));
  d.innerHTML=`${avatar}<div class="body"><div class="name">💬 ${safeName}</div><div class="msg">${safeMsg}</div><a href="${m.chat_url}">Open Message</a></div><button class="x" aria-label="Close">×</button>`;
  d.querySelector(".x").onclick=()=>d.remove();
  wrap.prepend(d);
  setTimeout(()=>{ if(d.isConnected)d.remove(); },12000);

  if(enabled() && "Notification" in window && Notification.permission==="granted" && document.hidden){
    try{
      const n=new Notification("New message • "+safeName,{
        body:m.message||"New CRM message",
        icon:m.photo_url||undefined,
        tag:"gaur-chat-"+m.id,
        renotify:true
      });
      n.onclick=()=>{window.focus();window.location.href=m.chat_url;n.close();};
      setTimeout(()=>n.close(),12000);
    }catch(e){}
  }
}

function badge(n){
  let b=document.getElementById("v42UnreadBadge");
  if(!b){b=document.createElement("div");b.id="v42UnreadBadge";b.className="v42-unread-badge";document.body.appendChild(b);}
  b.textContent=n>99?"99+":String(n);
  b.style.display=n>0?"flex":"none";
  const title=document.title.replace(/^\(\d+\+?\)\s*/,"");
  document.title=n>0?`(${n>99?"99+":n}) ${title}`:title;
}

async function poll(){
  if(polling)return; polling=true;
  try{
    const last=parseInt(localStorage.getItem(KEY_LAST)||"0",10)||0;
    const r=await fetch("/v4/chat/state?after_id="+encodeURIComponent(last),{credentials:"same-origin",cache:"no-store"});
    if(!r.ok){polling=false;return;}
    const j=await r.json();
    if(!j.authenticated){polling=false;return;}
    badge(j.unread||0);

    if(!baselineDone && last===0){
      localStorage.setItem(KEY_LAST,String(j.latest_id||0));
      baselineDone=true; polling=false; return;
    }
    baselineDone=true;

    if(Array.isArray(j.messages) && j.messages.length){
      j.messages.forEach(m=>toast(m));
      chime();
    }
    if((j.latest_id||0)>last)localStorage.setItem(KEY_LAST,String(j.latest_id||0));
  }catch(e){}
  polling=false;
}


function renameLegacyLauncher(){
  try{
    document.querySelectorAll("button,a,div,span").forEach(el=>{
      const t=(el.textContent||"").trim();
      if(t==="Chat Upp GYS"||t==="Open Chat Upp GYS"||t==="THE GAUR Chat"){
        if(t==="Open Chat Upp GYS")el.textContent="Open Lets Chat Upp!!!!";
        else el.textContent="Lets Chat Upp!!!!";
      }
    });
  }catch(e){}
}

function init(){
  ensureStyles();
  renameLegacyLauncher();
  enablePrompt();
  if(enabled()) unlockAudio();
  document.addEventListener("click",()=>{ if(enabled())unlockAudio(); },{passive:true});
  poll();
  setInterval(poll,POLL_MS);
  document.addEventListener("visibilitychange",()=>{ if(!document.hidden)poll(); });
  window.addEventListener("focus",poll);
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();
