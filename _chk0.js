
document.addEventListener("DOMContentLoaded",function(){
  var layout=document.querySelector(".layout");
  if(!layout)return;
  var tldrWrap=layout.querySelector(".layout-tldr");
  var items=Array.prototype.slice.call(layout.querySelectorAll(".section,.risk-warn"));
  if(items.length===0)return;
  var wides=new Set();
  items.forEach(function(s,i){if(s.dataset.span==="2")wides.add(i);});
  var rows=[];
  var i=0;
  while(i<items.length){
    if(wides.has(i)){
      var r=document.createElement("div");r.className="row";
      var c=document.createElement("div");c.className="col-full";
      c.appendChild(items[i]);r.appendChild(c);rows.push(r);i++;
    }else if(i+1<items.length&&!wides.has(i+1)){
      var r2=document.createElement("div");r2.className="row";
      var c1=document.createElement("div");var c2=document.createElement("div");
      c1.appendChild(items[i]);c2.appendChild(items[i+1]);
      r2.appendChild(c1);r2.appendChild(c2);rows.push(r2);i+=2;
    }else{
      var r3=document.createElement("div");r3.className="row";
      var c3=document.createElement("div");
      c3.appendChild(items[i]);r3.appendChild(c3);rows.push(r3);i++;
    }
  }
  layout.innerHTML="";
  if(tldrWrap)layout.appendChild(tldrWrap);
  rows.forEach(function(r){layout.appendChild(r);});
});

var shKline=[
{d:'06-29',o:4026.69,c:4073.90,h:4075.33,l:3992.55,a:16662},
{d:'06-30',o:4058.17,c:4094.40,h:4097.42,l:4052.17,a:15303},
{d:'07-01',o:4090.76,c:4112.45,h:4143.31,l:4087.54,a:16985},
{d:'07-02',o:4054.09,c:4028.90,h:4093.68,l:4019.21,a:15772},
{d:'07-03',o:4031.34,c:4043.64,h:4073.88,l:4027.26,a:14656},
{d:'07-06',o:4059.19,c:4041.24,h:4060.07,l:4005.41,a:14321},
{d:'07-07',o:4019.49,c:3990.24,h:4028.51,l:3971.71,a:11964},
{d:'07-08',o:3996.81,c:3970.88,h:4016.03,l:3967.91,a:11924},
{d:'07-09',o:3977.55,c:4036.59,h:4040.54,l:3938.88,a:13642},
{d:'07-10',o:4031.54,c:3996.16,h:4074.83,l:3995.81,a:15631},
{d:'07-13',o:3966.02,c:3913.79,h:3983.05,l:3900.67,a:13349},
{d:'07-14',o:3909.27,c:3967.13,h:3967.13,l:3869.30,a:12718},
{d:'07-15',o:3963.73,c:3955.58,h:3981.67,l:3943.70,a:12263},
{d:'07-16',o:3912.38,c:3882.41,h:3940.45,l:3867.60,a:11242},
{d:'07-17',o:3865.32,c:3764.15,h:3869.21,l:3745.17,a:12464},
{d:'07-20',o:3791.66,c:3796.28,h:3831.66,l:3741.11,a:12947},
{d:'07-21',o:3812.16,c:3864.37,h:3864.60,l:3743.36,a:13965},
{d:'07-22',o:3839.67,c:3867.03,h:3884.44,l:3839.67,a:12581},
{d:'07-23',o:3868.09,c:3876.78,h:3878.83,l:3851.71,a:10259},
{d:'07-24',o:3853.63,c:3814.20,h:3861.04,l:3808.64,a:9154},
{d:'07-27',o:3808.90,c:3858.25,h:3858.31,l:3793.45,a:10313},
{d:'07-28',o:3823.13,c:3813.31,h:3844.01,l:3797.37,a:9497},
{d:'07-29',o:3823.29,c:3828.47,h:3845.77,l:3782.48,a:10874},
{d:'07-30',o:3812.11,c:3804.69,h:3839.34,l:3767.50,a:11065},
{d:'07-31',o:3833.54,c:3832.26,h:3847.09,l:3822.37,a:11877},
{d:'08-03',o:3812.61,c:3809.66,h:3827.64,l:3797.64,a:9523},
{d:'08-04',o:3816.37,c:3822.28,h:3831.94,l:3799.52,a:10084},
{d:'08-05',o:3815.12,c:3878.43,h:3884.40,l:3815.12,a:12087},
{d:'08-06',o:3864.27,c:3900.35,h:3902.05,l:3864.27,a:11668},
{d:'08-07',o:3896.49,c:3940.04,h:3940.93,l:3885.62,a:12095}
];

var gzKline=[
{d:'06-29',o:11103.52,c:11062.33,h:11165.88,l:10826.96,a:9951},
{d:'06-30',o:11035.11,c:11335.65,h:11340.81,l:10987.85,a:9261},
{d:'07-01',o:11353.63,c:11462.91,h:11531.61,l:11342.27,a:10469},
{d:'07-02',o:11252.66,c:11192.79,h:11492.19,l:11158.32,a:9698},
{d:'07-03',o:11194.47,c:11189.64,h:11317.99,l:11104.42,a:9034},
{d:'07-06',o:11230.71,c:10990.10,h:11272.98,l:10939.34,a:8729},
{d:'07-07',o:10943.73,c:10719.78,h:11008.85,l:10674.24,a:7163},
{d:'07-08',o:10738.19,c:10485.82,h:10750.33,l:10477.39,a:6987},
{d:'07-09',o:10529.67,c:10690.70,h:10703.17,l:10277.24,a:7529},
{d:'07-10',o:10692.07,c:10604.18,h:10898.08,l:10604.18,a:8932},
{d:'07-13',o:10522.08,c:10047.39,h:10564.98,l:10020.65,a:7568},
{d:'07-14',o:10051.66,c:10204.30,h:10214.84,l:9849.87,a:6708},
{d:'07-15',o:10239.53,c:10090.29,h:10292.88,l:10048.49,a:6588},
{d:'07-16',o:9966.63,c:9880.07,h:10136.13,l:9830.79,a:6285},
{d:'07-17',o:9839.29,c:9271.69,h:9847.17,l:9246.30,a:6855},
{d:'07-20',o:9383.01,c:8982.84,h:9438.62,l:8809.67,a:6948},
{d:'07-21',o:8999.34,c:9305.66,h:9308.02,l:8571.20,a:7466},
{d:'07-22',o:9224.71,c:9187.62,h:9359.47,l:9131.89,a:6526},
{d:'07-23',o:9188.72,c:9259.74,h:9305.87,l:9134.58,a:5542},
{d:'07-24',o:9148.28,c:9000.00,h:9230.45,l:9000.00,a:5061},
{d:'07-27',o:8978.54,c:9306.25,h:9306.25,l:8969.07,a:5175},
{d:'07-28',o:9198.95,c:9085.66,h:9293.72,l:9043.12,a:5150},
{d:'07-29',o:9079.41,c:9144.23,h:9192.91,l:8918.45,a:5825},
{d:'07-30',o:9091.94,c:8866.24,h:9164.55,l:8812.46,a:5594},
{d:'07-31',o:9082.34,c:9130.20,h:9272.69,l:9082.34,a:6327},
{d:'08-03',o:9120.54,c:9163.45,h:9200.12,l:9106.70,a:5257},
{d:'08-04',o:9233.35,c:9430.38,h:9458.08,l:9201.93,a:5745},
{d:'08-05',o:9412.96,c:9707.01,h:9737.76,l:9412.96,a:6682},
{d:'08-06',o:9654.64,c:9784.07,h:9822.69,l:9652.24,a:7013},
{d:'08-07',o:9792.57,c:9971.30,h:9971.88,l:9663.84,a:7478}
];

var breadthData=[
{section:'涨停 Limit-up',count:75,flag:1},
{section:'>7%',count:206,flag:1},
{section:'5~7%',count:213,flag:1},
{section:'2~5%',count:807,flag:1},
{section:'0~2%',count:1555,flag:1},
{section:'平盘 Flat',count:147,flag:0},
{section:'0~2%',count:2119,flag:-1},
{section:'2~5%',count:365,flag:-1},
{section:'5~7%',count:26,flag:-1},
{section:'>7%',count:22,flag:-1},
{section:'跌停 Limit-down',count:4,flag:-1}
];

var sectorData=[
{name:'CRO',pct:10.63,lead:'博腾股份'},
{name:'医疗服务 Healthcare',pct:8.40,lead:'博腾股份'},
{name:'玻璃玻纤 Glass&Fiber',pct:7.11,lead:'中材科技'},
{name:'锗镓概念 Ge&Ga',pct:6.91,lead:'光智科技'},
{name:'元件 Components',pct:6.74,lead:'一博科技'},
{name:'电子布 E-glass',pct:6.64,lead:'中材科技'},
{name:'电子树脂 E-resin',pct:6.62,lead:'银禧科技'},
{name:'减肥药 GLP-1',pct:6.60,lead:'博腾股份'},
{name:'靶材 Targets',pct:6.11,lead:'有研新材'},
{name:'生物制品 Biologics',pct:6.06,lead:'近岸蛋白'}
];

var volFlowData=[
{d:'08-03',vol:9523,mainNet:-193.8,jumboNet:-180.3,chg:0.53},
{d:'08-04',vol:10084,mainNet:133.5,jumboNet:189.6,chg:0.33},
{d:'08-05',vol:12087,mainNet:327.0,jumboNet:373.7,chg:1.51},
{d:'08-06',vol:11668,mainNet:-84.6,jumboNet:-32.9,chg:0.18},
{d:'08-07',vol:12095,mainNet:226.6,jumboNet:243.7,chg:1.02}
];

var idxCards=[
{name:'上证指数',nameEn:'SSE Composite',price:3940.04,chg:1.02,chg5d:2.81},
{name:'国证2000',nameEn:'CNI 2000',price:9971.30,chg:1.91,chg5d:9.21},
{name:'深证成指',nameEn:'SZSE Component',price:14311.01,chg:1.42,chg5d:5.39},
{name:'创业板指',nameEn:'ChiNext',price:3563.12,chg:1.35,chg5d:6.55},
{name:'科创50',nameEn:'STAR 50',price:1744.02,chg:2.51,chg5d:6.61},
{name:'中证1000',nameEn:'CSI 1000',price:7679.53,chg:1.98,chg5d:8.54}
];

function calcMA(data,period){
var r=new Array(data.length).fill(null);
for(var i=period-1;i<data.length;i++){
var s=0;
for(var j=0;j<period;j++){s+=data[i-j].c;}
r[i]=s/period;
}
return r;
}

function drawKline(containerId,allData,displayCount,title){
var data=allData.slice(-displayCount);
var ma5=calcMA(allData,5).slice(-displayCount);
var ma20=calcMA(allData,20).slice(-displayCount);
var W=720,H=400,ml=55,mr=15,mt=30,mb=30;
var chartW=W-ml-mr,chartH=H-mt-mb;
var priceH=chartH*0.68,volH=chartH*0.27,gap=chartH*0.05;
var minP=Infinity,maxP=-Infinity;
for(var i=0;i<data.length;i++){
if(data[i].l<minP)minP=data[i].l;
if(data[i].h>maxP)maxP=data[i].h;
}
for(var i=0;i<ma5.length;i++){
if(ma5[i]!==null){
if(ma5[i]<minP)minP=ma5[i];
if(ma5[i]>maxP)maxP=ma5[i];
}
if(ma20[i]!==null){
if(ma20[i]<minP)minP=ma20[i];
if(ma20[i]>maxP)maxP=ma20[i];
}
}
var pad=(maxP-minP)*0.05;minP-=pad;maxP+=pad;
var maxVol=0;
for(var i=0;i<data.length;i++){if(data[i].a>maxVol)maxVol=data[i].a;}
var n=data.length;
var slotW=chartW/n,candleW=slotW*0.6;
function py(p){return mt+(maxP-p)/(maxP-minP)*priceH;}
function vy(v){return mt+priceH+gap+volH-(v/maxVol*volH);}
function cx(i){return ml+i*slotW+slotW*0.2;}
var volTop=mt+priceH+gap;
var s='<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">';
s+='<rect width="'+W+'" height="'+H+'" fill="#1e293b" rx="8"/>';
s+='<text x="'+ml+'" y="'+(mt-10)+'" fill="#e2e8f0" font-size="12" font-weight="bold">'+title+'</text>';
for(var g=0;g<=4;g++){
var gy=mt+g*priceH/4;
var gp=maxP-g*(maxP-minP)/4;
s+='<line x1="'+ml+'" y1="'+gy+'" x2="'+(W-mr)+'" y2="'+gy+'" stroke="#334155" stroke-width="0.5" stroke-dasharray="2,3"/>';
s+='<text x="'+(ml-5)+'" y="'+(gy+4)+'" fill="#64748b" font-size="10" text-anchor="end" font-family="monospace">'+gp.toFixed(0)+'</text>';
}
s+='<line x1="'+ml+'" y1="'+volTop+'" x2="'+(W-mr)+'" y2="'+volTop+'" stroke="#334155" stroke-width="0.5"/>';
for(var i=0;i<n;i++){
var d=data[i];
var up=d.c>=d.o;
var color=up?'#ef4444':'#22c55e';
var x=cx(i);
var bodyTop=py(Math.max(d.o,d.c));
var bodyBottom=py(Math.min(d.o,d.c));
var bodyH=Math.max(bodyBottom-bodyTop,1);
s+='<line x1="'+(x+candleW/2)+'" y1="'+py(d.h)+'" x2="'+(x+candleW/2)+'" y2="'+py(d.l)+'" stroke="'+color+'" stroke-width="1"/>';
s+='<rect x="'+x+'" y="'+bodyTop+'" width="'+candleW+'" height="'+bodyH+'" fill="'+color+'" rx="1"/>';
s+='<rect x="'+x+'" y="'+vy(d.a)+'" width="'+candleW+'" height="'+(volTop+volH-vy(d.a))+'" fill="'+color+'" opacity="0.35" rx="1"/>';
if(i%2===0||i===n-1){
s+='<text x="'+(x+candleW/2)+'" y="'+(H-6)+'" fill="#64748b" font-size="9" text-anchor="middle">'+d.d+'</text>';
}
}
var ma5Path='';
for(var i=0;i<n;i++){
if(ma5[i]!==null){
ma5Path+=(ma5Path?' L':'M')+(cx(i)+candleW/2)+' '+py(ma5[i]);
}
}
if(ma5Path)s+='<path d="'+ma5Path+'" stroke="#f59e0b" stroke-width="1.5" fill="none"/>';
var ma20Path='';
for(var i=0;i<n;i++){
if(ma20[i]!==null){
ma20Path+=(ma20Path?' L':'M')+(cx(i)+candleW/2)+' '+py(ma20[i]);
}
}
if(ma20Path)s+='<path d="'+ma20Path+'" stroke="#3b82f6" stroke-width="1.5" fill="none"/>';
s+='<text x="'+(W-mr-5)+'" y="'+(mt+10)+'" fill="#f59e0b" font-size="10" text-anchor="end">MA5</text>';
s+='<text x="'+(W-mr-40)+'" y="'+(mt+10)+'" fill="#3b82f6" font-size="10" text-anchor="end">MA20</text>';
s+='</svg>';
document.getElementById(containerId).innerHTML=s;
}

function drawBreadth(containerId,data){
var W=720,H=300,ml=90,mr=60,mt=20,mb=20;
var chartW=W-ml-mr,chartH=H-mt-mb;
var maxCount=0;
for(var i=0;i<data.length;i++){if(data[i].count>maxCount)maxCount=data[i].count;}
var n=data.length;
var barH=chartH/n*0.7;
var gapH=chartH/n*0.3;
var s='<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">';
s+='<rect width="'+W+'" height="'+H+'" fill="#1e293b" rx="8"/>';
for(var i=0;i<n;i++){
var d=data[i];
var color=d.flag>0?'#ef4444':(d.flag<0?'#22c55e':'#64748b');
var y=mt+i*(chartH/n)+gapH/2;
var w=d.count/maxCount*chartW;
s+='<text x="'+(ml-5)+'" y="'+(y+barH/2+4)+'" fill="#94a3b8" font-size="10" text-anchor="end">'+d.section+'</text>';
s+='<rect x="'+ml+'" y="'+y+'" width="'+w+'" height="'+barH+'" fill="'+color+'" opacity="0.8" rx="2"/>';
s+='<text x="'+(ml+w+5)+'" y="'+(y+barH/2+4)+'" fill="'+color+'" font-size="11" font-weight="bold">'+d.count+'</text>';
}
s+='</svg>';
document.getElementById(containerId).innerHTML=s;
}

function drawSectorRank(containerId,data,title){
var W=720,H=300,ml=120,mr=110,mt=25,mb=15;
var chartW=W-ml-mr,chartH=H-mt-mb;
var maxPct=0;
for(var i=0;i<data.length;i++){if(data[i].pct>maxPct)maxPct=data[i].pct;}
var n=data.length;
var barH=chartH/n*0.7;
var gapH=chartH/n*0.3;
var s='<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">';
s+='<rect width="'+W+'" height="'+H+'" fill="#1e293b" rx="8"/>';
s+='<text x="'+ml+'" y="'+(mt-8)+'" fill="#e2e8f0" font-size="12" font-weight="bold">'+title+'</text>';
for(var i=0;i<n;i++){
var d=data[i];
var y=mt+i*(chartH/n)+gapH/2;
var w=d.pct/maxPct*chartW;
s+='<text x="'+(ml-5)+'" y="'+(y+barH/2+4)+'" fill="#94a3b8" font-size="10" text-anchor="end">'+d.name+'</text>';
s+='<rect x="'+ml+'" y="'+y+'" width="'+w+'" height="'+barH+'" fill="#ef4444" opacity="0.8" rx="2"/>';
s+='<text x="'+(ml+w+5)+'" y="'+(y+barH/2+4)+'" fill="#ef4444" font-size="11" font-weight="bold">+'+d.pct+'%</text>';
s+='<text x="'+(W-mr+5)+'" y="'+(y+barH/2+4)+'" fill="#64748b" font-size="9">'+d.lead+'</text>';
}
s+='</svg>';
document.getElementById(containerId).innerHTML=s;
}

function drawStrength(containerId,shAll,gzAll,displayCount){
var sh=shAll.slice(-displayCount);
var gz=gzAll.slice(-displayCount);
var W=720,H=220,ml=50,mr=15,mt=20,mb=25;
var chartW=W-ml-mr,chartH=H-mt-mb;
var shBase=sh[0].c,gzBase=gz[0].c;
var shNorm=[],gzNorm=[];
for(var i=0;i<sh.length;i++){
shNorm.push(100*sh[i].c/shBase);
gzNorm.push(100*gz[i].c/gzBase);
}
var allVals=shNorm.concat(gzNorm);
var minV=Math.min.apply(null,allVals);
var maxV=Math.max.apply(null,allVals);
var padV=(maxV-minV)*0.1;minV-=padV;maxV+=padV;
var n=sh.length;
var slotW=chartW/(n-1);
function vy(v){return mt+(maxV-v)/(maxV-minV)*chartH;}
function vx(i){return ml+i*slotW;}
var s='<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">';
s+='<rect width="'+W+'" height="'+H+'" fill="#1e293b" rx="8"/>';
s+='<text x="'+ml+'" y="'+(mt-6)+'" fill="#e2e8f0" font-size="11" font-weight="bold">Relative Strength (normalized to 100)</text>';
for(var g=0;g<=4;g++){
var gy=mt+g*chartH/4;
var gv=maxV-g*(maxV-minV)/4;
s+='<line x1="'+ml+'" y1="'+gy+'" x2="'+(W-mr)+'" y2="'+gy+'" stroke="#334155" stroke-width="0.5" stroke-dasharray="2,3"/>';
s+='<text x="'+(ml-5)+'" y="'+(gy+4)+'" fill="#64748b" font-size="9" text-anchor="end" font-family="monospace">'+gv.toFixed(0)+'</text>';
}
s+='<line x1="'+ml+'" y1="'+vy(100)+'" x2="'+(W-mr)+'" y2="'+vy(100)+'" stroke="#475569" stroke-width="1"/>';
var shPath='';
for(var i=0;i<n;i++){shPath+=(shPath?' L':'M')+vx(i)+' '+vy(shNorm[i]);}
s+='<path d="'+shPath+'" stroke="#3b82f6" stroke-width="2" fill="none"/>';
var gzPath='';
for(var i=0;i<n;i++){gzPath+=(gzPath?' L':'M')+vx(i)+' '+vy(gzNorm[i]);}
s+='<path d="'+gzPath+'" stroke="#ef4444" stroke-width="2" fill="none"/>';
for(var i=0;i<n;i+=3){
s+='<text x="'+vx(i)+'" y="'+(H-6)+'" fill="#64748b" font-size="9" text-anchor="middle">'+sh[i].d+'</text>';
}
s+='<text x="'+(W-mr-5)+'" y="'+(mt+10)+'" fill="#3b82f6" font-size="10" text-anchor="end">SH Composite ('+shNorm[n-1].toFixed(1)+')</text>';
s+='<text x="'+(W-mr-5)+'" y="'+(mt+24)+'" fill="#ef4444" font-size="10" text-anchor="end">CNI 2000 ('+gzNorm[n-1].toFixed(1)+')</text>';
s+='</svg>';
document.getElementById(containerId).innerHTML=s;
}

function drawVolFlow(containerId,data){
var W=720,H=280,ml=50,mr=50,mt=25,mb=30;
var chartW=W-ml-mr,chartH=H-mt-mb;
var volH=chartH*0.45,flowH=chartH*0.45,gap=chartH*0.1;
var n=data.length;
var slotW=chartW/n,barW=slotW*0.5;
var maxVol=0;
for(var i=0;i<n;i++){if(data[i].vol>maxVol)maxVol=data[i].vol;}
var absMaxFlow=0;
for(var i=0;i<n;i++){
if(Math.abs(data[i].mainNet)>absMaxFlow)absMaxFlow=Math.abs(data[i].mainNet);
if(Math.abs(data[i].jumboNet)>absMaxFlow)absMaxFlow=Math.abs(data[i].jumboNet);
}
var volTop=mt,flowTop=mt+volH+gap;
function volY(v){return volTop+volH-(v/maxVol*volH);}
function flowY(v){return flowTop+flowH/2-(v/absMaxFlow*flowH/2);}
function cx(i){return ml+i*slotW+slotW*0.25;}
var s='<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;height:auto" xmlns="http://www.w3.org/2000/svg">';
s+='<rect width="'+W+'" height="'+H+'" fill="#1e293b" rx="8"/>';
s+='<text x="'+ml+'" y="'+(mt-8)+'" fill="#e2e8f0" font-size="12" font-weight="bold">Volume & Main Fund Flow (5D)</text>';
for(var g=0;g<=2;g++){
var gy=volTop+g*volH/2;
var gv=maxVol*(1-g/2);
s+='<line x1="'+ml+'" y1="'+gy+'" x2="'+(W-mr)+'" y2="'+gy+'" stroke="#334155" stroke-width="0.5" stroke-dasharray="2,3"/>';
s+='<text x="'+(ml-5)+'" y="'+(gy+4)+'" fill="#64748b" font-size="9" text-anchor="end" font-family="monospace">'+(gv/1000).toFixed(1)+'k</text>';
}
s+='<line x1="'+ml+'" y1="'+flowTop+'" x2="'+(W-mr)+'" y2="'+flowTop+'" stroke="#475569" stroke-width="1"/>';
s+='<line x1="'+ml+'" y1="'+(flowTop+flowH/2)+'" x2="'+(W-mr)+'" y2="'+(flowTop+flowH/2)+'" stroke="#334155" stroke-width="0.5" stroke-dasharray="2,3"/>';
s+='<text x="'+(ml-5)+'" y="'+(flowTop+flowH/2+4)+'" fill="#64748b" font-size="9" text-anchor="end">0</text>';
for(var i=0;i<n;i++){
var d=data[i];
var x=cx(i);
var volColor=d.chg>=0?'#ef4444':'#22c55e';
s+='<rect x="'+x+'" y="'+volY(d.vol)+'" width="'+barW+'" height="'+(volTop+volH-volY(d.vol))+'" fill="'+volColor+'" opacity="0.5" rx="2"/>';
s+='<text x="'+(x+barW/2)+'" y="'+(volY(d.vol)-4)+'" fill="'+volColor+'" font-size="9" text-anchor="middle" font-weight="bold">'+(d.vol/1000).toFixed(1)+'k</text>';
var mainColor=d.mainNet>=0?'#ef4444':'#22c55e';
var jumboColor=d.jumboNet>=0?'#f59e0b':'#64748b';
var mainY=flowY(d.mainNet);
var mainBase=flowY(0);
var mainH=Math.abs(mainY-mainBase);
var mainYPos=Math.min(mainY,mainBase);
s+='<rect x="'+x+'" y="'+mainYPos+'" width="'+(barW*0.45)+'" height="'+mainH+'" fill="'+mainColor+'" opacity="0.8" rx="1"/>';
var jumboY=flowY(d.jumboNet);
var jumboBase=flowY(0);
var jumboH=Math.abs(jumboY-jumboBase);
var jumboYPos=Math.min(jumboY,jumboBase);
s+='<rect x="'+(x+barW*0.5)+'" y="'+jumboYPos+'" width="'+(barW*0.45)+'" height="'+jumboH+'" fill="'+jumboColor+'" opacity="0.8" rx="1"/>';
s+='<text x="'+(x+barW/2)+'" y="'+(H-8)+'" fill="#94a3b8" font-size="10" text-anchor="middle">'+d.d+'</text>';
if(d.mainNet>=0){
s+='<text x="'+(x+barW*0.225)+'" y="'+(mainYPos-3)+'" fill="'+mainColor+'" font-size="8" text-anchor="middle">+'+d.mainNet.toFixed(0)+'</text>';
}else{
s+='<text x="'+(x+barW*0.225)+'" y="'+(mainYPos+mainH+9)+'" fill="'+mainColor+'" font-size="8" text-anchor="middle">'+d.mainNet.toFixed(0)+'</text>';
}
}
s+='<rect x="'+(W-mr-45)+'" y="'+(mt+5)+'" width="8" height="8" fill="#ef4444" opacity="0.8" rx="1"/>';
s+='<text x="'+(W-mr-33)+'" y="'+(mt+12)+'" fill="#94a3b8" font-size="9">Main</text>';
s+='<rect x="'+(W-mr-45)+'" y="'+(mt+18)+'" width="8" height="8" fill="#f59e0b" opacity="0.8" rx="1"/>';
s+='<text x="'+(W-mr-33)+'" y="'+(mt+25)+'" fill="#94a3b8" font-size="9">Jumbo</text>';
s+='</svg>';
document.getElementById(containerId).innerHTML=s;
}

function renderIdxCards(){
var html='';
for(var i=0;i<idxCards.length;i++){
var idx=idxCards[i];
var cls=idx.chg>=0?'red':'green';
var sign=idx.chg>=0?'+':'';
html+='<div class="idx-card">';
html+='<div class="name"><span class="cn-text">'+idx.name+'</span><span class="en-text">'+idx.nameEn+'</span></div>';
html+='<div class="price '+cls+'">'+idx.price.toFixed(2)+'</div>';
html+='<div class="chg '+cls+'">'+sign+idx.chg.toFixed(2)+'%</div>';
html+='<div class="chg5d">5D: <span style="color:'+(idx.chg5d>=0?'var(--red)':'var(--green)')+'">'+(idx.chg5d>=0?'+':'')+idx.chg5d.toFixed(2)+'%</span></div>';
html+='</div>';
}
document.getElementById('idxGrid').innerHTML=html;
}

function toggleLang(){
document.body.classList.toggle('lang-en');
}

function init(){
renderIdxCards();
drawKline('shChart',shKline,15,'SSE Composite / \u4e0a\u8bc1\u6307\u6570');
drawKline('gzChart',gzKline,15,'CNI 2000 / \u56fd\u8bc12000');
drawBreadth('breadthChart',breadthData);
drawSectorRank('sectorChart',sectorData,'Top 10 Sectors / \u677f\u5757\u6da8\u5e45TOP10');
drawStrength('strengthChart',shKline,gzKline,15);
drawVolFlow('volChart',volFlowData);
}
window.onload=init;
