(function(root){
const trigrams={'111':'乾','000':'坤','101':'離','010':'坎','011':'巽','100':'震','001':'艮','110':'兌'};
function change(total,left){if(!Number.isInteger(total)||total<4||!Number.isInteger(left)||left<1||left>total-2)throw Error('Invalid split');const right=total-left-1,a=left%4||4,b=right%4||4;return {total,left,right,human:1,a,b,removed:a+b+1,remaining:total-a-b-1};}
function identify(lines,changed=false){if(lines.length!==6)throw Error('Six lines required');const bits=lines.map(n=>{if(![6,7,8,9].includes(n))throw Error('Invalid line');return changed?(n===6?1:n===9?0:n%2):n%2;});return trigrams[bits.slice(3).join('')]+'上'+trigrams[bits.slice(0,3).join('')]+'下';}
function randomSplit(total){const max=total-2,limit=Math.floor(4294967296/max)*max;let n;do{n=crypto.getRandomValues(new Uint32Array(1))[0];}while(n>=limit);return 1+n%max;}
const api={change,identify,randomSplit};if(typeof module!=='undefined')module.exports=api;else root.Yarrow=api;
})(globalThis);
