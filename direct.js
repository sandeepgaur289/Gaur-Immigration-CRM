
function gaurDirectWhatsAppShare(){
 var t=document.querySelector('h1.title')||document.querySelector('main h1')||document.querySelector('main h2');
 var page=(t?t.textContent:document.title).replace(/\s+/g,' ').trim();
 var msg='THE GAUR CRM\nReport/Page: '+page+'\nLink: '+location.href;
 window.open('https://wa.me/?text='+encodeURIComponent(msg),'_blank','noopener');
}
function gaurDirectExcelExport(){
 var main=document.querySelector('main');
 if(!main)return;
 var clone=main.cloneNode(true);
 clone.querySelectorAll('.no-print,script,button,input,select,textarea').forEach(function(x){x.remove();});
}
