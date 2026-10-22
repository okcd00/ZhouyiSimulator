/* Delegated feedback also covers dynamically created export buttons. */
(()=>{
  let effectsEnabled=true, audio, gestureId=0;
  const replay=new WeakSet(),pending=new WeakSet();
  const toggle=document.createElement('button');
  toggle.id='brushSound';toggle.textContent='笔音 · 开';toggle.setAttribute('aria-pressed','true');
  toggle.title='点击落笔音效（独立于背景音乐）';
  document.querySelector('nav').append(toggle);
  toggle.onclick=()=>{effectsEnabled=!effectsEnabled;toggle.textContent='笔音 · '+(effectsEnabled?'开':'关');toggle.setAttribute('aria-pressed',String(effectsEnabled));};
  function brushSound(){
    if(!effectsEnabled)return;
    try{
      audio??=new AudioContext();if(audio.state==='suspended')audio.resume().catch(()=>{});
      const t=audio.currentTime,duration=.65;
      // Filtered noise follows the soft drag of a wet brush across paper.
      const buffer=audio.createBuffer(1,Math.ceil(audio.sampleRate*duration),audio.sampleRate),data=buffer.getChannelData(0);
      for(let i=0;i<data.length;i++)data[i]=Math.random()*2-1;
      const source=audio.createBufferSource(),filter=audio.createBiquadFilter(),gain=audio.createGain();source.buffer=buffer;
      filter.type='bandpass';filter.frequency.setValueAtTime(1700,t);filter.frequency.exponentialRampToValueAtTime(650,t+duration);filter.Q.value=.8;
      gain.gain.setValueAtTime(.0001,t);gain.gain.exponentialRampToValueAtTime(.12,t+.045);gain.gain.exponentialRampToValueAtTime(.045,t+.25);gain.gain.exponentialRampToValueAtTime(.075,t+.43);gain.gain.exponentialRampToValueAtTime(.0001,t+duration);
      source.connect(filter).connect(gain).connect(audio.destination);source.start(t);source.stop(t+duration);
      // A low, brief accent marks the brush touching the paper.
      const o=audio.createOscillator(),v=audio.createGain();o.frequency.setValueAtTime(260,t);o.frequency.exponentialRampToValueAtTime(130,t+.12);
      v.gain.setValueAtTime(.045,t);v.gain.exponentialRampToValueAtTime(.0001,t+.18);o.connect(v).connect(audio.destination);o.start(t);o.stop(t+.2);
    }catch{/* Visual feedback and the action remain available without audio. */}
  }
  document.addEventListener('click',event=>{
    const button=event.target.closest?.('button.primary');
    if(!button||button.disabled)return;
    if(replay.has(button))return;
    event.preventDefault();event.stopImmediatePropagation();
    if(pending.has(button))return;
    pending.add(button);button.classList.add('is-inking');button.setAttribute('aria-busy','true');brushSound();
    const box=button.getBoundingClientRect(),svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('viewBox','0 0 320 100');svg.setAttribute('preserveAspectRatio','none');svg.setAttribute('aria-hidden','true');svg.classList.add('ink-gesture');
    svg.style.left=(box.left-9)+'px';svg.style.top=(box.top-3)+'px';svg.style.width=(box.width+18)+'px';svg.style.height=(box.height+6)+'px';
    const stroke='M269 17C221 3 118 4 59 20C16 32 8 53 33 70C65 94 166 96 240 81C291 71 313 51 293 31C286 24 271 20 256 17';
    const ns='http://www.w3.org/2000/svg',id='brush-mask-'+(++gestureId);
    const make=(tag,attrs)=>{const el=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,String(v)));return el;};
    const guide=make('path',{d:stroke});
    svg.append(guide);
    // Put the gesture in the dialog top layer when a modal is open.
    (button.closest('dialog')||document.body).append(svg);
    const length=guide.getTotalLength(),samples=200,points=[];
    for(let i=0;i<=samples;i++){
      const t=i/samples,at=guide.getPointAtLength(t*length),before=guide.getPointAtLength(Math.max(0,t*length-.6)),after=guide.getPointAtLength(Math.min(length,t*length+.6));
      const dx=after.x-before.x,dy=after.y-before.y,n=Math.hypot(dx,dy)||1;
      // Heavy landing, pressed belly, then a dry lifting tip.
      const pressure=(12.8*Math.pow(1-t,.85)+.65)*(1+.1*Math.sin(t*19));
      const grain=.5*Math.sin(i*2.7)+.22*Math.sin(i*7.1);
      points.push({x:at.x,y:at.y,nx:-dy/n,ny:dx/n,w:pressure/2+grain,t});
    }
    guide.remove();
    const defs=make('defs',{}),mask=make('mask',{id,maskUnits:'userSpaceOnUse',x:-20,y:-20,width:360,height:140});
    mask.append(make('path',{d:stroke,pathLength:1000,stroke:'white','stroke-width':25,fill:'none',class:'ink-reveal'}));defs.append(mask);svg.append(defs);
    const pigment=make('g',{mask:'url(#'+id+')'});
    const edge=(p,sign)=>[p.x+p.nx*p.w*sign,p.y+p.ny*p.w*sign].join(',');
    for(let i=0;i<samples;i++){
      const a=points[i],b=points[i+1];
      pigment.append(make('polygon',{points:[edge(a,1),edge(b,1),edge(b,-1),edge(a,-1)].join(' '),fill:i%4===0?'#bd4a33':'#ca553b',opacity:.96-.78*Math.pow(a.t,1.65)}));
    }
    // Fine separated hairs leave streaks and dry-brush gaps toward the tail.
    for(let f=0;f<7;f++){
      const offset=(f-3)/3.4;
      const d=points.map((p,i)=>(i?'L':'M')+(p.x+p.nx*p.w*offset).toFixed(2)+' '+(p.y+p.ny*p.w*offset).toFixed(2)).join(' ');
      pigment.append(make('path',{d,fill:'none',stroke:f%2?'#e99a64':'#612b22','stroke-width':f%2?.38:.55,opacity:.28,'stroke-dasharray':f%2?'7 4 2 6':'12 3 1 5'}));
    }
    svg.append(pigment);
    const dot=make('g',{class:'ink-landing'});
    dot.append(make('ellipse',{cx:269,cy:17,rx:8.5,ry:6,fill:'#b53d2b',transform:'rotate(18 269 17)'}));
    dot.append(make('ellipse',{cx:267,cy:15.5,rx:5,ry:3.4,fill:'#d56040',opacity:.65}));
    dot.append(make('circle',{cx:279,cy:13,r:1.3,fill:'#b94a32',opacity:.5}));svg.append(dot);
    const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
    setTimeout(()=>{
      svg.remove();button.classList.remove('is-inking');button.removeAttribute('aria-busy');pending.delete(button);
      if(!button.isConnected||button.disabled)return;
      replay.add(button);try{button.click();}finally{replay.delete(button);}
    },reduced?90:930);
  },true);
})();
