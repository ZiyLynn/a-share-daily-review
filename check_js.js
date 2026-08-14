const fs = require('fs');
const html = fs.readFileSync('技术面复盘_20260813.html', 'utf8');
const scripts = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map(m => m[1]).filter(s => s.trim());
let allOK = true;
scripts.forEach((s, i) => {
  try {
    new Function(s);
    console.log('Script ' + (i+1) + ': OK (' + s.length + ' chars)');
  } catch(e) {
    allOK = false;
    console.log('Script ' + (i+1) + ': ERROR - ' + e.message);
  }
});
console.log(allOK ? 'ALL JS CHECKS PASSED' : 'JS CHECKS FAILED');
