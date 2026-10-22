const fs = require('node:fs');
const path = require('node:path');
const base = path.resolve(__dirname, '../references');
const entries = fs.readFileSync(path.join(base,'易经标题目录.txt'),'utf8').trim().split(/\r?\n/).map(line => {const [id,title,name,full,raw] = line.split('_');return {id:Number(id),title,name,full,key:raw==='坎上下坤'?'坎上坤下':raw,text:fs.readFileSync(path.join(base,line),'utf8')};});
fs.writeFileSync(path.join(__dirname,'data.js'),'window.HEXAGRAMS = '+JSON.stringify(entries)+';\n');
console.log('Imported',entries.length,'hexagrams');
