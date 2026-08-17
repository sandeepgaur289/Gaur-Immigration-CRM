

(function(){
 function getText(el,sel,def){var x=el&&el.querySelector(sel);return x?(x.textContent||'').trim():def;}
 function build(){
  try{
   if(location.pathname!='/dashboard')return;
   if(document.getElementById('mdMergedPerformance')||document.getElementById('gmV392Panel'))return;
   var old=document.getElementById('competitionLiveBar');
   var today=document.querySelector('.today-report-wrap.luxury-today-report');
   if(!old||!today)return;
   var cards=today.querySelectorAll('.today-company-card');
   if(cards.length!==1)return;
   var card=cards[0],stats=card.querySelectorAll('.today-stat-grid > div');
   if(stats.length<2)return;
   var scLogo=old.querySelector('.team-live.scic img'),wwLogo=old.querySelector('.team-live.wwic img');
   if(!scLogo||!wwLogo)return;
   var company=card.classList.contains('today-scic-card')?'SMART CHOICE':'WHITE WAVE';
   var enroll=getText(stats[0],'b','0'),revenue=getText(stats[1],'b','₹0'),date=getText(today,'.today-report-head small','');

   var panel=document.createElement('section');
   panel.id='gmV392Panel';
   panel.innerHTML=`
    <div class="g392-head"><b>● LIVE PERFORMANCE + TODAY'S REPORT</b><small>${date}</small></div>
    <div class="g392-main">
      <div class="g392-team">
        <div class="g392-logo"><img src="${scLogo.src}"></div>
        <div class="g392-core"><div class="g392-crown">♛</div><div class="g392-name">SMART CHOICE</div><div class="g392-stars">★★★★★</div><div id="g392Sc" class="g392-score">0</div><div class="g392-label">OVERALL LIVE PERFORMANCE</div><div class="g392-meter"><i id="g392Sm"></i></div></div>
      </div>
      <div class="g392-vs">VS</div>
      <div class="g392-team right">
        <div class="g392-core"><div class="g392-crown">♛</div><div class="g392-name">WHITE WAVE</div><div class="g392-stars">★★★★★</div><div id="g392Ww" class="g392-score">0</div><div class="g392-label">OVERALL LIVE PERFORMANCE</div><div class="g392-meter blue"><i id="g392Wm"></i></div></div>
        <div class="g392-logo white"><img src="${wwLogo.src}"></div>
      </div>
    </div>
    <div class="g392-today">
      <div class="g392-today-title">◆ ${company}<small>YOUR COMPANY • TODAY</small></div>
      <div class="g392-cards">
        <div class="g392-card"><span>Today's Enrollments</span><b>${enroll}</b></div>
        <div class="g392-card"><span>Today's Revenue</span><b>${revenue}</b></div>
        <div class="g392-card date"><span>Performance Date</span><b>${date}</b></div>
      </div>
    </div>
    <div class="g392-live">▥ &nbsp; LIVE PERFORMANCE &nbsp; ▥</div>`;
   old.parentNode.insertBefore(panel,old);
   document.body.classList.add('gm-v392-ready');

   function sync(){
    var a=document.getElementById('scicLiveScore'),b=document.getElementById('wwicLiveScore');
    var am=document.getElementById('scicMeter'),bm=document.getElementById('wwicMeter');
    var da=document.getElementById('g392Sc'),db=document.getElementById('g392Ww'),dm1=document.getElementById('g392Sm'),dm2=document.getElementById('g392Wm');
    if(a&&da)da.textContent=a.textContent;if(b&&db)db.textContent=b.textContent;
    if(am&&dm1)dm1.style.width=am.style.width||'0%';if(bm&&dm2)dm2.style.width=bm.style.width||'0%';
   }
   sync();setInterval(sync,1000);
  }catch(e){console.error('GM merged dashboard skipped',e);}
 }
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',function(){setTimeout(build,100);});
 else setTimeout(build,100);
})();

