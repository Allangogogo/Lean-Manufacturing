// 06-标准作业与安灯详解.pptx - Standard Work & Andon for Fastener Manufacturing
const PptxGenJS = require("pptxgenjs");
const path = require("path");
const OUT = __dirname;
let pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE"; pptx.title = "标准作业与安灯详解"; pptx.author = "精益工具知识库";
const S = pptx.ShapeType;
const P="1E2761",SC="CADCFC",AC="FFFFFF",BG="F8FAFC",T="1E293B",TL="64748B",G="059669",WA="D97706",D="DC2626",TE="0D9488";
const W=13.33,HT=7.5;
function setBg(s){s.background={color:BG};}
function addTopBar(s,c,h){s.addShape(S.rect,{x:0,y:0,w:W,h:h||0.06,fill:{color:c},line:{color:c}});}
function addTitleBand(s,t,sub){
  s.addShape(S.rect,{x:0,y:0.05,w:W,h:1.5,fill:{color:P},line:{color:P}});
  s.addText(t,{x:0.8,y:0.12,w:W-1.2,h:0.75,fontSize:28,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addText(sub,{x:0.8,y:0.85,w:W-1.2,h:0.45,fontSize:14,color:SC,fontFace:"Microsoft YaHei",valign:"middle"});
}
function addFooter(s,txt){
  var fy=HT-0.35; s.addShape(S.rect,{x:0,y:fy,w:W,h:0.35,fill:{color:P},line:{color:P}});
  s.addText(txt,{x:0.5,y:fy+0.01,w:W-1,h:0.3,fontSize:9,color:"94A3B8",fontFace:"Microsoft YaHei",valign:"middle"});
  s.addText("06  |  标准作业与安灯详解",{x:0.5,y:fy+0.01,w:W-1,h:0.3,fontSize:9,color:"94A3B8",fontFace:"Microsoft YaHei",align:"right",valign:"middle"});
}
function addCard(s,x,y,w,h,title,body,barColor){
  s.addShape(S.roundRect,{x,y,w,h,fill:{color:AC},line:{color:"E2E8F0",width:1},rectRadius:0.08});
  s.addShape(S.rect,{x:x+0.02,y:y+0.2,w:w-0.04,h:h-0.18,fill:{color:AC},line:{color:AC}});
  s.addShape(S.roundRect,{x,y,w,h:0.22,fill:{color:barColor},line:{color:barColor},rectRadius:0.08});
  s.addShape(S.rect,{x:x+0.02,y:y+0.15,w:w-0.04,h:0.1,fill:{color:AC},line:{color:AC}});
  s.addText(title,{x:x+0.2,y:y+0.26,w:w-0.4,h:0.4,fontSize:13,bold:true,color:T,fontFace:"Microsoft YaHei",valign:"middle"});
  if(body&&body.length>0){s.addText(body,{x:x+0.2,y:y+0.7,w:w-0.4,h:h-1.0,valign:"top",lineSpacingMultiple:1.15,fontSize:9.5,color:TL,fontFace:"Microsoft YaHei"});}
}
function statCard(s,x,y,w,num,label,color){
  s.addShape(S.roundRect,{x,y,w,h:1.05,fill:{color:color},line:{color:color},rectRadius:0.1});
  s.addText(num,{x,y:y+0.06,w,h:0.55,fontSize:24,bold:true,color:AC,fontFace:"Arial",align:"center",valign:"middle"});
  s.addText(label,{x,y:y+0.58,w,h:0.38,fontSize:9.5,color:AC,fontFace:"Microsoft YaHei",align:"center",valign:"middle"});
}
function drawRow(s,x,y,w,h,cells,cw,bg,isH){
  s.addShape(S.rect,{x,y,w,h,fill:{color:bg},line:{color:"E2E8F0",width:0.5}});
  var cx=x; cells.forEach(function(c,i){ s.addText(c,{x:cx+0.05,y:y+0.04,w:cw[i]-0.1,h:h-0.08,fontSize:isH?10:9.5,bold:!!isH,color:isH?AC:T,fontFace:"Microsoft YaHei",align:i===0?"left":"center",valign:"middle"}); cx+=cw[i]; });
}

// ========== SLIDE 1: Chapter Cover ==========

(function(){
  var s=pptx.addSlide(); setBg(s,P);
  s.addShape(S.ellipse,{x:-1.5,y:0.8,w:6,h:6,fill:{color:"1A3A6B",transparency:55}});
  s.addShape(S.ellipse,{x:10,y:-0.2,w:5,h:5,fill:{color:"1A3A6B",transparency:55}});
  s.addText("06",{x:0.8,y:1.5,w:4,h:2.5,fontSize:100,bold:true,color:SC,fontFace:"Arial",valign:"middle",transparency:18});
  s.addShape(S.rect,{x:0.8,y:4.1,w:5.5,h:0.05,fill:{color:TE},line:{color:TE}});
  s.addText("标准作业与安灯详解",{x:0.8,y:4.25,w:12,h:1.1,fontSize:38,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addText("Standard Work & Andon System  |  紧固件制造专用",{x:0.8,y:5.3,w:12,h:0.6,fontSize:16,color:SC,fontFace:"Microsoft YaHei",valign:"middle"});
})();

// ========== SLIDE 2: 标准作业三要素 ==========

(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,P,0.06);
  addTitleBand(s,"标准作业三要素","Three Elements of Standard Work");
  addFooter(s,"标准作业  |  Standard Work");
  var cW=3.85,cH=4.5,gap=0.22,sX=0.4,cY=2.1;
  addCard(s,sX,cY,cW,cH,"节拍时间  Takt Time",[
    {text:"定义: 生产一个产品的必需时间",bold:true},{text:""},
    {text:"公式:"},{text:"Takt = 可用时间 / 客户需求数量",color:T},{text:""},
    {text:"紧固件案例:",bold:true},{text:"可用时间 = 480 - 30 = 450 min"},
    {text:"客户需求 = 18,000 件/天"},{text:"Takt = 450 / 18000 = 1.5 秒/件",color:G,bold:true},
    {text:""},{text:"意味着每1.5秒产出一个螺栓"}
  ],P);
  addCard(s,sX+cW+gap,cY,cW,cH,"作业循环  Work Sequence",[
    {text:"定义: 操作员在节拍内的标准步骤",bold:true},{text:""},
    {text:"内容:"},{text:"操作员的操作顺序",bullet:true},
    {text:"手持半成品的标准WIP",bullet:true},{text:"机器自动运行时间",bullet:true},
    {text:""},{text:"紧固件案例:",bold:true},{text:"冷镦: 送料成形冲裁收集"},
    {text:"每个动作精确到秒，无浪费",color:G},{text:""},{text:"作业顺序 = 最佳动作序列"}
  ],TE);
  addCard(s,sX+(cW+gap)*2,cY,cW,cH,"标准WIP  Standard WIP",[
    {text:"定义: 维持循环的最小在制品",bold:true},{text:""},
    {text:"包括:"},{text:"工序间库存",bullet:true},{text:"夹具上待加工品",bullet:true},{text:"自动运行中的半成品",bullet:true},
    {text:""},{text:"紧固件案例:",bold:true},{text:"冷镦自动运行: 约200件"},
    {text:"搓丝缓冲: 约50件"},{text:"检测等待: 约20件"},
    {text:"标准WIP = 270件",color:G,bold:true}
  ],WA);
  s.addShape(S.roundRect,{x:0.5,y:cY+cH+0.18,w:W-1,h:0.42,fill:{color:"E0E7FF"},line:{color:"C7D2FE"},rectRadius:0.08});
  s.addText("标准作业 = Takt Time + Work Sequence + Standard WIP",{x:0.8,y:cY+cH+0.2,w:W-1.6,h:0.38,fontSize:11,bold:true,color:P,fontFace:"Microsoft YaHei",align:"center",valign:"middle"});
})();

// ========== SLIDE 3: 标准作业组合表 ==========

(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,P,0.06);
  addTitleBand(s,"标准作业组合表","Standard Work Combination Chart");
  addFooter(s,"标准作业  |  Standard Work");
  var cw=[2.3,1.7,1.7,1.7,1.7],tw=9.7,th=0.42,tY=2.2;
  drawRow(s,0.5,tY,tw,th,["作业要素","作业时间(s)","机器时间(s)","步行时间(s)","结束时间(s)"],cw,P,true);
  var rows=[
    ["送料至冷镦机","0.5","0","0","0.5"],["冷镦自动成形","0.3","4.2","0","4.5"],
    ["离开模具","0.4","0","0.3","4.9"],["收集成品","0.6","0","0.2","5.5"],
    ["走至打孔区","0.8","0","0.5","6.3"],["打孔后重新开始","0.4","3.8","0","6.7"]
  ];
  var cy2=tY+th;
  rows.forEach(function(r,i){drawRow(s,0.5,cy2,tw,th,r,cw,i%2===0?AC:"F1F5F9",false);cy2+=th;});
  var gx=10.8,gy=2.2;
  s.addShape(S.roundRect,{x:gx-0.1,y:gy-0.3,w:2.2,h:3.8,fill:{color:"E0E7FF"},line:{color:"C7D2FE"},rectRadius:0.08});
  s.addText("时间对比",{x:gx,y:gy-0.2,w:2,h:0.3,fontSize:10,bold:true,color:P,fontFace:"Microsoft YaHei",align:"center"});
  var bars=[{l:"作业",t:2.0,c:P},{l:"机器",t:8.0,c:TE},{l:"步行",t:1.0,c:WA}];
  var by=gy+0.2;
  bars.forEach(function(d){
    s.addText(d.l,{x:gx,y:by,w:0.5,h:0.3,fontSize:8,color:T,fontFace:"Microsoft YaHei",align:"center"});
    s.addShape(S.roundRect,{x:gx+0.5,y:by+0.04,w:d.t*0.2,h:0.22,fill:{color:d.c},line:{color:d.c},rectRadius:0.04});
    s.addText(d.t+"s",{x:gx+0.5+d.t*0.2+0.04,y:by,w:0.5,h:0.3,fontSize:8,color:d.c,fontFace:"Microsoft YaHei"});
    by+=0.4;
  });
  s.addText("Takt=1.5s",{x:gx,y:by+0.1,w:2,h:0.3,fontSize:9,bold:true,color:D,fontFace:"Microsoft YaHei",align:"center"});
  s.addShape(S.rect,{x:gx+0.1,y:by+0.35,w:0.33,h:0.03,fill:{color:D},line:{color:D}});
})();

// ========== SLIDE 4: 标准作业与改善 ==========

(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,P,0.06);
  addTitleBand(s,"标准作业与改善","Standard Work & Kaizen");
  addFooter(s,"标准作业  |  Standard Work");
  addCard(s,0.5,1.8,3.8,2.5,"工作标准化  Standardized Work",
    [{text:"每一项作业都建立标准",bold:true},{text:""},{text:". 明确每个动作的顺序"},
     {text:". 规定时间标准"},{text:". 消除个人差异"},{text:""},{text:"紧固件: 冷镦作业标准书",color:G}],P);
  addCard(s,4.95,1.8,3.8,2.5,"设备改善  Equipment Kaizen",
    [{text:"让设备更好配合标准作业",bold:true},{text:""},{text:". 减少机器等待时间"},
     {text:". 优化换模流程"},{text:". 提升自动化水平"},{text:""},{text:"紧固件: 快速换模<10min",color:G}],TE);
  addCard(s,9.4,1.8,3.5,2.5,"布局优化  Layout Optimization",
    [{text:"减少搬运和步行浪费",bold:true},{text:""},{text:". U型产线布局"},
     {text:". 零件就近供应"},{text:". 消除交叉物流"},{text:""},{text:"紧固件: 连续流布局",color:G}],WA);
  var iy=4.6,steps=["制定SOP","培训执行","发现问题","改善标准"];
  var sColors=[P,TE,G,WA],sx2=[0.6,3.8,7.0,10.2],sw=2.0,sh=1.3;
  steps.forEach(function(step,i){
    s.addShape(S.roundRect,{x:sx2[i],y:iy,w:sw,h:sh,fill:{color:sColors[i]},line:{color:sColors[i]},rectRadius:0.12});
    s.addText(step,{x:sx2[i],y:iy,w:sw,h:sh,fontSize:11,bold:true,color:AC,fontFace:"Microsoft YaHei",align:"center",valign:"middle"});
    if(i<3){s.addShape(S.rightArrow,{x:sx2[i]+sw+0.08,y:iy+sh/2-0.18,w:0.7,h:0.36,fill:{color:TL},line:{color:TL}});}
  });
  s.addShape(S.roundRect,{x:0.5,y:iy+sh+0.25,w:W-1,h:0.38,fill:{color:"E0E7FF"},line:{color:"C7D2FE"},rectRadius:0.08});
  s.addText("标准不是终点，而是改善的起点",{x:0.8,y:iy+sh+0.27,w:W-1.6,h:0.34,fontSize:11,bold:true,color:P,fontFace:"Microsoft YaHei",align:"center",valign:"middle"});
})();

// ========== SLIDE 5: 安灯系统概述 ==========

(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,TE,0.06);
  addTitleBand(s,"安灯系统概述","Andon System Overview");
  addFooter(s,"安灯  |  Andon System");
  addCard(s,0.5,1.8,5.5,2.2,"什么是安灯  |  What is Andon",
    [{text:"安灯(Andon)源自日语'灯光'，是一种视觉管理系统。"},
     {text:"当产线出现异常(质量/设备/物料/安全)，操作员通过拉绳或按钮"},
     {text:"触发光信号和声音通知，使问题可视化并快速响应。"}],TE);
  addCard(s,6.5,1.8,6.3,3.55,"升级协议  |  Escalation Protocol",
    [{text:"L1 班组长  <30秒  —  现场立即处理，规定时间内解决"},
     {text:"L2 主管  <2分钟  —  30s未解决，调配资源跨线支援"},
     {text:"L3 经理  <5分钟  —  2min未解决，产线可能停线，启动应急"}],P);
  statCard(s,0.5,4.3,1.75,"30秒","级别1响应",G);
  statCard(s,2.45,4.3,1.75,"2分钟","级别2响应",WA);
  statCard(s,4.4,4.3,1.75,"5分钟","级别3响应",D);
  statCard(s,6.35,4.3,1.75,"100%","问题可见性",P);
})();

// ========== SLIDE 6: 安灯实施步骤 ==========

(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,TE,0.06);
  addTitleBand(s,"安灯实施步骤","Andon Implementation Steps");
  addFooter(s,"安灯  |  Andon System");
  var steps2=[
    {x:0.4,t:"需求评估",st:"Assessment",c:P,d:"分析产线痛点 统计异常类型 确定优先级"},
    {x:4.7,t:"方案设计",st:"Design",c:TE,d:"确定触发条件 设计安灯板布局 制定升级规则"},
    {x:9.0,t:"设备安装",st:"Install",c:"6369E9",d:"安装拉绳/按钮 配置灯光系统 连接声音报警"},
    {x:0.4,t:"人员培训",st:"Train",c:"7C3AED",d:"操作员响应训练 升级流程演练 角色职责明确"},
    {x:4.7,t:"试运行",st:"Pilot",c:WA,d:"选择试点产线 收集反馈数据 优化触发阈值"},
    {x:9.0,t:"全面推广",st:"Scale",c:G,d:"复制到所有产线 建立数据分析 持续改善循环"}
  ];
  steps2.forEach(function(step,i){
    var row=Math.floor(i/3), sy=1.75+row*1.65;
    s.addShape(S.roundRect,{x:step.x,y:sy,w:3.8,h:1.45,fill:{color:step.c},line:{color:step.c},rectRadius:0.1});
    s.addText(step.t,{x:step.x+0.15,y:sy+0.1,w:3.5,h:0.35,fontSize:12,bold:true,color:AC,fontFace:"Microsoft YaHei"});
    s.addText(step.st,{x:step.x+0.15,y:sy+0.4,w:3.5,h:0.2,fontSize:8,color:AC,fontFace:"Arial",transparency:50});
    s.addText(step.d,{x:step.x+0.15,y:sy+0.65,w:3.5,h:0.6,fontSize:8.5,color:AC,fontFace:"Microsoft YaHei",lineSpacingMultiple:1.25});
    if(i!==2&&i<5){ s.addShape(S.rightArrow,{x:step.x+3.8+0.05,y:sy+0.72-0.15,w:0.4,h:0.3,fill:{color:TL},line:{color:TL}}); }
  });
  var tY2=5.3;
  s.addText("触发条件",{x:0.5,y:tY2-0.28,w:8,h:0.28,fontSize:10,bold:true,color:TE,fontFace:"Microsoft YaHei"});
  var tcw=[2.0,1.8,2.2,2.2,2.5],ttw=10.7;
  drawRow(s,0.5,tY2,ttw,0.28,["异常类型","触发信号","响应级别","响应时间","典型案例"],tcw,P,true);
  var trows=[
    ["质量问题","黄灯","Level 1","< 30s","螺栓头部开裂"],
    ["设备故障","红灯","Level 2","< 2min","冷镦机卡料"],
    ["物料短缺","黄闪","Level 2","< 2min","线材不足"],
    ["安全问题","红灯+声音","Level 3","< 5min","操作员受伤"]
  ];
  var tcy2=tY2+0.28;
  trows.forEach(function(r,i){drawRow(s,0.5,tcy2,ttw,0.28,r,tcw,i%2===0?"EFF6FF":"F8FAFC",false);tcy2+=0.28;});
})();

// ========== SLIDE 7: 安灯数据分析 ==========

(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,TE,0.06);
  addTitleBand(s,"安灯数据分析","Andon Data Analysis");
  addFooter(s,"安灯  |  Andon System");
  statCard(s,0.5,1.7,2.5,"248","本月安灯触发次数",P);
  statCard(s,3.3,1.7,2.5,"87%","产线正常运行时间",G);
  statCard(s,6.1,1.7,2.5,"1.2min","平均响应时间",TE);
  statCard(s,8.9,1.7,2.5,"15","月度改善项目数",WA);
  s.addText("安灯频率帕累托分析  |  Pareto Analysis",{x:0.5,y:3.0,w:8,h:0.3,fontSize:11,bold:true,color:TE,fontFace:"Microsoft YaHei"});
  var issues=["设备故障","质量异常","物料短缺","换模超时","安全问题"];
  var freqs=[45,28,15,8,4];
  var pcolors=[D,P,WA,TE,TL];
  var barH=0.26,barGap=0.08,bY2=3.5,bX2=2.0,bW2=4.0;
  issues.forEach(function(issue,i){
    var w=(freqs[i]/50)*bW2;
    s.addText(issue,{x:0.5,y:bY2+i*(barH+barGap),w:1.5,h:barH,fontSize:9,color:T,fontFace:"Microsoft YaHei",align:"right",valign:"middle"});
    s.addShape(S.roundRect,{x:bX2,y:bY2+i*(barH+barGap)+0.03,w:w,h:barH-0.06,fill:{color:pcolors[i]},line:{color:pcolors[i]},rectRadius:0.04});
    s.addText(freqs[i]+"次",{x:bX2+w+0.1,y:bY2+i*(barH+barGap),w:0.8,h:barH,fontSize:9,bold:true,color:pcolors[i],fontFace:"Arial",valign:"middle"});
  });
  // PDCA loop
  var lcx=10.5, lcy=4.0, lR=0.9;
  s.addText("改善循环  |  Improvement Cycle",{x:7.5,y:3.0,w:5.5,h:0.3,fontSize:11,bold:true,color:TE,fontFace:"Microsoft YaHei",align:"center"});
  s.addShape(S.diamond,{x:lcx-0.3,y:lcy-0.3,w:0.6,h:0.6,fill:{color:"E0E7FF"},line:{color:"C7D2FE"}});
  s.addText("PDCA",{x:lcx-0.3,y:lcy-0.3,w:0.6,h:0.6,fontSize:10,bold:true,color:P,fontFace:"Arial",align:"center",valign:"middle"});
  var loopItems=[
    {t:"触发安灯",c:P,x:lcx,y:lcy-lR*1.15},
    {t:"问题分析",c:TE,x:lcx+lR*1.2,y:lcy},
    {t:"制定对策",c:G,x:lcx,y:lcy+lR*1.15},
    {t:"标准更新",c:WA,x:lcx-lR*1.2,y:lcy}
  ];
  loopItems.forEach(function(item){
    s.addShape(S.ellipse,{x:item.x-0.5,y:item.y-0.35,w:1.0,h:0.7,fill:{color:item.c},line:{color:item.c}});
    s.addText(item.t,{x:item.x-0.5,y:item.y-0.35,w:1.0,h:0.7,fontSize:8.5,bold:true,color:AC,fontFace:"Microsoft YaHei",align:"center",valign:"middle"});
  });
  // Arrows
  s.addShape(S.rightArrow,{x:lcx+0.3,y:lcy-lR*0.55-0.12,w:lR*0.65,h:0.24,fill:{color:TL},line:{color:TL}});
  s.addShape(S.rect,{x:lcx+lR*0.55,y:lcy+0.3,w:0.24,h:lR*0.55,fill:{color:TL},line:{color:TL}});
  s.addShape(S.rightArrow,{x:lcx+lR*0.55,y:lcy+0.2,w:lR*0.7,h:0.24,fill:{color:TL},line:{color:TL},rotation:90});
  s.addShape(S.rightArrow,{x:lcx-lR*0.55-0.24,y:lcy+0.35,w:lR*0.65,h:0.24,fill:{color:TL},line:{color:TL}});
  s.addShape(S.rightArrow,{x:lcx-lR*0.55-0.24,y:lcy-lR*0.55-0.12,w:lR*0.65,h:0.24,fill:{color:TL},line:{color:TL}});
  s.addShape(S.roundRect,{x:0.5,y:6.3,w:W-1,h:0.5,fill:{color:"E0E7FF"},line:{color:"C7D2FE"},rectRadius:0.08});
  s.addText("设备故障(45%)和质量异常(28%)占安灯触发73%，应优先改善",{x:0.8,y:6.32,w:W-1.6,h:0.45,fontSize:11,bold:true,color:P,fontFace:"Microsoft YaHei",align:"center",valign:"middle"});
})();

// ========== SLIDE 8: Summary ==========

(function(){
  var s=pptx.addSlide(); setBg(s,"0F172A");
  s.addShape(S.rect,{x:0,y:0,w:W,h:0.08,fill:{color:TE},line:{color:TE}});
  s.addText("06",{x:0.5,y:0.5,w:3,h:2,fontSize:72,bold:true,color:SC,fontFace:"Arial",valign:"middle",transparency:20});
  s.addText("总结  |  Summary",{x:4.0,y:0.6,w:8,h:0.5,fontSize:24,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  addCard(s,0.5,1.5,5.8,4.2,"标准作业  Standard Work",
    [{text:"三要素: Takt Time + 作业循环 + 标准WIP"},
     {text:"组合表实现人机时间最优配比"},{text:"作业标准化是改善的基石"},
     {text:"U型布局减少搬运和步行"},{text:"快速换模保障柔性生产"},
     {text:"可视化让异常无处藏身"}],P);
  addCard(s,6.8,1.5,6.0,4.2,"安灯  Andon System",
    [{text:"拉绳触发，问题30秒内可见"},
     {text:"三级升级: 班长(30s)主管(2m)经理(5m)"},
     {text:"触发条件: 质量/设备/物料/安全"},
     {text:"帕累托分析锁定关键改善方向"},
     {text:"PDCA循环驱动持续改善"},
     {text:"数据化追踪安灯响应效率"}],TE);
  s.addShape(S.rect,{x:0,y:HT-0.55,w:W,h:0.55,fill:{color:"0F172A"},line:{color:"0F172A"}});
  s.addText("标准化是改善的起点，安灯是质量的守护者  |  Standard Work + Andon = 精益基石",
    {x:1,y:HT-0.5,w:W-2,h:0.45,fontSize:12,color:TE,fontFace:"Microsoft YaHei",align:"center",valign:"middle",bold:true});
})();

// ===== Generate =====

pptx.writeFile({ fileName: path.join(OUT, "06-标准作业与安灯详解.pptx") }).then(function(r){
  console.log("Done:", r);
}).catch(function(e){ console.error("Error:", e); process.exit(1); });
