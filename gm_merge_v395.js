

(function(){
 function txt(root,sel,def){var x=root&&root.querySelector(sel);return x?(x.textContent||'').trim():def;}
 function buildGM(){
  try{
   if(location.pathname!='/dashboard')return;
   if(document.getElementById('mdMergedPerformance')||document.getElementById('gmV395Merged'))return;

   var oldBar=document.getElementById('competitionLiveBar');
   var today=document.querySelector('.today-report-wrap.luxury-today-report');
   if(!oldBar||!today)return;

   var single=today.querySelector('.today-company-grid.single');
   if(!single)return; /* GM only */
   var card=single.querySelector('.today-company-card');
   if(!card)return;

   var stats=card.querySelectorAll('.today-stat-grid > div');
   if(stats.length<2)return;

   var scLogo=oldBar.querySelector('.team-live.scic img');
   var wwLogo=oldBar.querySelector('.team-live.wwic img');
   if(!scLogo||!wwLogo)return;

   var company=card.classList.contains('today-scic-card')?'SMART CHOICE':'WHITE WAVE';
   var enroll=txt(stats[0],'b','0');
   var revenue=txt(stats[1],'b','₹0');
   var date=txt(today,'.today-report-head small','');

   var panel=document.createElement('section');
   panel.id='gmV395Merged';
   panel.innerHTML=`
     <div class="g395-top"><b>● LIVE PERFORMANCE + TODAY'S REPORT</b><small>${date}</small></div>
     <div class="g395-live-grid">
       <div class="g395-team">
         <div class="g395-logo"><img src="${scLogo.src}" alt="Smart Choice"></div>
         <div class="g395-core">
           <div class="g395-crown">♛</div><div class="g395-name">SMART CHOICE</div><div class="g395-stars">★★★★★</div>
           <div id="g395ScScore" class="g395-score">0</div><div class="g395-score-label">OVERALL LIVE PERFORMANCE</div>
           <div class="g395-meter"><i id="g395ScMeter"></i></div>
         </div>
       </div>
       <div class="g395-vs">VS</div>
       <div class="g395-team right">
         <div class="g395-core">
           <div class="g395-crown">♛</div><div class="g395-name">WHITE WAVE</div><div class="g395-stars">★★★★★</div>
           <div id="g395WwScore" class="g395-score">0</div><div class="g395-score-label">OVERALL LIVE PERFORMANCE</div>
           <div class="g395-meter blue"><i id="g395WwMeter"></i></div>
         </div>
         <div class="g395-logo white"><img src="${wwLogo.src}" alt="White Wave"></div>
       </div>
     </div>
     <div class="g395-today">
       <div class="g395-today-title">◆ ${company}<small>YOUR COMPANY • TODAY</small></div>
       <div class="g395-today-grid">
         <div class="g395-card"><span>Today's Enrollments</span><b>${enroll}</b></div>
         <div class="g395-card"><span>Today's Revenue</span><b>${revenue}</b></div>
         <div class="g395-card date"><span>Performance Date</span><b>${date}</b></div>
       </div>
     </div>
     <div class="g395-live-pill">▥ &nbsp; LIVE PERFORMANCE &nbsp; ▥</div>`;

   oldBar.parentNode.insertBefore(panel,oldBar);

   function sync(){
     var sc=document.getElementById('scicLiveScore'),ww=document.getElementById('wwicLiveScore');
     var sm=document.getElementById('scicMeter'),wm=document.getElementById('wwicMeter');
     var ds=document.getElementById('g395ScScore'),dw=document.getElementById('g395WwScore');
     var dsm=document.getElementById('g395ScMeter'),dwm=document.getElementById('g395WwMeter');
     if(sc&&ds)ds.textContent=sc.textContent;
     if(ww&&dw)dw.textContent=ww.textContent;
     if(sm&&dsm)dsm.style.width=sm.style.width||'0%';
     if(wm&&dwm)dwm.style.width=wm.style.width||'0%';
   }
   sync();setInterval(sync,1000);
   document.body.classList.add('gm-v395-ready');
  }catch(e){console.error('v3.95 GM merge skipped',e);}
 }

 if(document.readyState==='loading'){
   document.addEventListener('DOMContentLoaded',function(){setTimeout(buildGM,120);});
 }else{
   setTimeout(buildGM,120);
 }
})();

