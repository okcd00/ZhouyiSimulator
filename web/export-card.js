/* Local, deterministic artwork composed from the user's reading. */
const saveReadingText = $('export').onclick;
let cardPreviewURL;
function downloadReading(blob, extension, reading) {
  const url=URL.createObjectURL(blob), link=document.createElement('a');
  link.href=url;link.download=`蓍境-${lookup(reading.lines,false).name}-${reading.date.slice(0,10)}.${extension}`;
  link.click();setTimeout(()=>URL.revokeObjectURL(url),3000);
}
function wrapCardText(context, text, width) {
  const rows=[];
  for(const paragraph of String(text).split(/\r?\n/)) {
    let row='';
    for(const ch of paragraph){if(row&&context.measureText(row+ch).width>width){rows.push(row);row=ch;}else row+=ch;}
    rows.push(row);
  }
  return rows;
}
async function createReadingCard(reading) {
  await document.fonts.ready;
  const c=document.createElement('canvas'),g=c.getContext('2d');
  const W=1200, margin=110, width=W-margin*2;
  const serif='"STKaiti", "KaiTi", "SimSun", serif', brush='"STXingkai", "STKaiti", "KaiTi", serif';
  const a=lookup(reading.lines,false),b=lookup(reading.lines,true);
  g.font=`30px ${serif}`;
  const question=wrapCardText(g,reading.question||'未设问 · 静观此刻',width);
  const verses=a.text.split(/\r?\n/).filter(x=>/^(初[九六]|[九六][二三四五]|上[九六])[：:]/.test(x));
  const changing=reading.lines.flatMap((n,i)=>n===6||n===9?[{i,n}]:[]);
  const movingRows=changing.length?changing.flatMap(({i,n})=>wrapCardText(g,`${positions[i]}爻 · ${names[n]}变${n===6?'阳':'阴'}　${verses[i]||'参见本卦经文。'}`,width)):['六爻皆静。本卦与之卦相同，静观卦辞与象辞。'];
  const judgement=wrapCardText(g,a.text.split(/\r?\n/)[0],width);
  const H=1740+question.length*44+movingRows.length*46+judgement.length*44;
  c.width=W;c.height=H;
  g.fillStyle='#0b2421';g.fillRect(0,0,W,H);
  try {
    const bg=new Image();bg.src='assets/sanctuary.png';await bg.decode();
    const scale=Math.max(W/bg.width,1000/bg.height);
    g.drawImage(bg,(W-bg.width*scale)/2,0,bg.width*scale,bg.height*scale);
  } catch { /* Solid ink background also supports offline image failure. */ }
  let shade=g.createLinearGradient(0,0,0,1100);shade.addColorStop(0,'#09231e22');shade.addColorStop(.5,'#0b242190');shade.addColorStop(1,'#0b2421');g.fillStyle=shade;g.fillRect(0,0,W,1100);
  g.strokeStyle='#c9a86566';g.lineWidth=1;g.strokeRect(42,42,W-84,H-84);g.strokeStyle='#c9a86525';g.strokeRect(52,52,W-104,H-104);
  // Subtle deterministic paper flecks, so every download has the same finish.
  for(let i=0;i<3400;i++){const x=(i*7919)%W,y=(i*1543)%H;g.fillStyle=i%2?'#f1d5a008':'#0000000c';g.fillRect(x,y,1+(i%2),1);}
  const text=(s,x,y,size=30,color='#ded8c4',font=serif)=>{g.font=`${size}px ${font}`;g.fillStyle=color;g.fillText(s,x,y);};
  text('蓍 境   /   THE YARROW RITUAL',margin,125,20,'#d8bf8d','sans-serif');
  text('一念一卦',margin,300,94,'#f0e4c7',brush);
  text('问于山水，留于此笺。',margin,370,29,'#c4cdbd');
  const date=new Date(reading.date).toLocaleString('zh-CN',{year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'});
  text(date,margin,429,21,'#afb8a4','sans-serif');
  // Cinnabar seal.
  g.save();g.translate(1007,280);g.rotate(.06);g.strokeStyle='#c46a4c';g.lineWidth=3;g.strokeRect(-35,-45,70,90);text('一',-19,-7,36,'#df926c',brush);text('念',-19,29,36,'#df926c',brush);g.restore();
  let y=530;
  text('此 刻 所 问',margin,y,19,'#c7aa71','sans-serif');y+=58;
  question.forEach(row=>{text(row,margin,y);y+=44;});
  y+=45;
  const top=y;
  function drawHexagram(x,hex,changed,label){
    text(label,x,top,20,'#c3a973','sans-serif');
    const left=x+22, bar=250, gap=40;
    reading.lines.forEach((n,i)=>{
      const yang=changed?(n===6?true:n===9?false:n%2===1):n%2===1;
      const py=top+52+(5-i)*35;
      g.fillStyle='#ddc28a';if(yang)g.fillRect(left,py,bar,12);else{g.fillRect(left,py,(bar-gap)/2,12);g.fillRect(left+(bar+gap)/2,py,(bar-gap)/2,12);}
      if(!changed&&(n===6||n===9)){g.beginPath();g.strokeStyle='#d57755';g.lineWidth=2;g.arc(left+bar+29,py+6,7,0,2*Math.PI);g.stroke();}
    });
    text(hex.full,x,top+333,50,'#eddbb2',brush);
    text(`第 ${hex.id} 卦 · ${hex.key}`,x,top+382,23,'#aab9a7');
  }
  drawHexagram(margin+55,a,false,'本 卦 / 当下之象');drawHexagram(710,b,true,'之 卦 / 变化之象');
  text('→',570,top+160,38,'#b36a4f');
  y=top+455;
  const rule=()=>{g.strokeStyle='#c9a86544';g.beginPath();g.moveTo(margin,y);g.lineTo(W-margin,y);g.stroke();};rule();y+=65;
  text('卦 辞 · 本 卦',margin,y,20,'#c7aa71','sans-serif');y+=55;
  judgement.forEach(row=>{text(row,margin,y);y+=44;});y+=38;rule();y+=65;
  text('动 爻 · 变化所在',margin,y,20,'#c7aa71','sans-serif');y+=58;
  movingRows.forEach(row=>{text(row,margin,y,30,'#d7d5c0');y+=46;});
  y+=55;
  text('六爻自下而上  /  '+reading.lines.map(n=>n+' '+names[n]).join(' · '),margin,y,21,'#a6b5a3');
  text('三变生爻 · 六爻为卦',margin,H-155,23,'#c9ad77');
  text('以经典为镜，照见当下。',margin,H-109,22,'#9aab98');
  text('SHIJING / 蓍境',W-330,H-109,19,'#c7aa71','sans-serif');
  return new Promise((resolve,reject)=>c.toBlob(blob=>blob?resolve(blob):reject(Error('图片编码失败')),'image/png'));
}
$('export').onclick=()=>{
  const reading=structuredClone(state);
  if(cardPreviewURL){URL.revokeObjectURL(cardPreviewURL);cardPreviewURL=null;}
  openDialog('<div class="eyebrow">KEEP THIS MOMENT / 留住此刻</div><h2>留一纸，或藏一境。</h2><p class="muted">文本保留完整经文与十八变记录；图片将这一卦绘成山水收藏笺。</p><div class="export-choices"><button id="saveText" class="primary">留下墨迹</button><button id="makeCard" class="primary">绘成卦笺</button></div><div id="cardPreview" aria-live="polite"></div>');
  $('saveText').onclick=saveReadingText;
  $('makeCard').onclick=async()=>{
    const button=$('makeCard'),target=$('cardPreview');button.disabled=true;button.textContent='正在落笔…';
    target.innerHTML='<p class="muted">正在绘制高清卦笺，所问与卦象仅在本机处理。</p>';
    try{
      const blob=await createReadingCard(reading);
      if(!target.isConnected)return;
      cardPreviewURL=URL.createObjectURL(blob);
      target.innerHTML='<img class="reading-card-preview" alt="山水卦笺预览，包含所问、本卦、之卦与动爻"><button id="downloadCard" class="primary">收藏图片 ↓</button><p class="muted">1200 像素宽 · 高清 PNG · 长文自动延展</p>';
      target.querySelector('img').src=cardPreviewURL;
      $('downloadCard').onclick=()=>downloadReading(blob,'png',reading);
      button.textContent='卦笺已绘成';
    }catch(error){target.textContent='卦笺暂未绘成，请重试；也可以先留下文本。';button.disabled=false;button.textContent='重新绘制';}
  };
};
