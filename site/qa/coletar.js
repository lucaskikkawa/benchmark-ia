const { chromium } = require('/node_modules/playwright-core');
const fs=require('fs'),path=require('path');const SITE=path.join(__dirname,'..','index.html');
const out={};
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
for(const [vn,vp,mob] of [['mobile',{width:390,height:844},true],['desktop',{width:1440,height:900},false]]){
 const p=await b.newPage({viewport:vp,isMobile:mob,hasTouch:mob});const log=[];
 p.on('console',m=>log.push(m.type()+': '+m.text()));p.on('pageerror',e=>log.push('pageerror: '+e.message));
 p.on('request',r=>{const u=r.url();if(!/^(file|data|blob):/.test(u))log.push('REDE: '+u)});
 await p.goto('file://'+SITE);await p.waitForTimeout(1200);const O=out[vn]={estados:{}};
 const cap=async(nome)=>{await p.waitForTimeout(600);
  const info=await p.evaluate((W)=>{const vis=e=>e.offsetParent!==null;const over=[];
   document.querySelectorAll('body *').forEach(e=>{if(!vis(e))return;const r=e.getBoundingClientRect();if(r.width>0&&(r.right>W+1||r.left<-1))over.push(e.tagName+'#'+e.id+'.'+e.className+' ['+Math.round(r.left)+','+Math.round(r.right)+']');
    if(e.scrollWidth>e.clientWidth+2&&getComputedStyle(e).overflowX==='hidden'&&e.children.length===0)over.push('CORTADO '+e.tagName+'.'+e.className+': '+e.textContent.slice(0,60))});
   const sel=s=>[...document.querySelectorAll(s)].filter(vis);
   return {scrollW:document.documentElement.scrollWidth,
    lista:sel('#lista .lr:not(.oculto)').map(e=>e.dataset.me+' '+(e.querySelector('.sc b')||{}).textContent+(e.querySelector('.selo')&&vis(e.querySelector('.selo'))?' SELO:'+e.querySelector('.selo').textContent:'')),
    nvSegVisivel:!!document.querySelector('#nvSeg')&&vis(document.querySelector('#nvSeg')),
    selosVisiveis:sel('.selo').map(e=>e.textContent),
    texto:(sel('main')[0]||document.body).innerText.slice(0,12000),overflow:over.slice(0,40)}},vp.width);
  O.estados[nome]=info;await p.screenshot({path:path.join(__dirname,`qa-${vn}-${nome}.png`),fullPage:true});};
 const go=async a=>{await p.click(`#nav button[data-aba=${a}]`);};
 for(const cen of ['A','B']){await p.click('#cen'+cen);
  const nvs=cen==='B'?['i','ii']:[null];
  for(const nv of nvs){if(nv)await p.click(`#nvSeg button[data-nv=${nv}]`);
   for(const a of ['ranking','comparar','esforco','tarefas','juizes']){await go(a);await cap(`${cen}${nv?'-'+nv:''}-${a}`);}
   await go('ranking');}}
 await p.click('#cenA');await go('ranking');
 await p.$eval('#slider',s=>{s.value=100;s.dispatchEvent(new Event('input',{bubbles:true}))});await cap('A-slider100');
 await p.$eval('#slider',s=>{s.value=0;s.dispatchEvent(new Event('input',{bubbles:true}))});await cap('A-slider0');
 await p.click('#btReset');await p.click('#cenB');await p.$eval('#slider',s=>{s.value=100;s.dispatchEvent(new Event('input',{bubbles:true}))});await cap('B-slider100');
 O.console=log;await p.close();}
await b.close();fs.writeFileSync(path.join(__dirname,'coleta.json'),JSON.stringify(out,null,1));})();
