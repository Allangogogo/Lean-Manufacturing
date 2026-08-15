// 07-deep-dive.js - Deep Dive Research PPTX
const PptxGenJS = require("pptxgenjs");
const path = require("path");
const OUT = __dirname;
let pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE"; pptx.title = "深度专题研究"; pptx.author = "精益工具知识库";
const S = pptx.ShapeType;
const P="1E2761", SC="CADCFC", AC="FFFFFF", BG="F8FAFC", T="1E293B", TL="64748B";
const G="059669", WA="D97706", D="DC2626", TE="0D9488", TL2="5EEAD4";
const W=13.33, HT=7.5;

function setBg(s){ s.background={color:BG}; }
function addTopBar(s,c,h){
  s.addShape(S.rect,{x:0,y:0,w:W,h:h||0.06,fill:{color:c},line:{color:c}});
}
function addTitleBand(s,t,sub){
  s.addShape(S.rect,{x:0,y:0.05,w:W,h:1.5,fill:{color:P},line:{color:P}});
  s.addText(t,{x:0.8,y:0.12,w:W-1.2,h:0.75,fontSize:28,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addText(sub,{x:0.8,y:0.85,w:W-1.2,h:0.45,fontSize:14,color:SC,fontFace:"Microsoft YaHei",valign:"middle"});
}
function addFooter(s,txt){
  var fy=HT-0.35;
  s.addShape(S.rect,{x:0,y:fy,w:W,h:0.35,fill:{color:P},line:{color:P}});
  s.addText(txt,{x:0.5,y:fy+0.01,w:W-1,h:0.3,fontSize:9,color:"94A3B8",fontFace:"Microsoft YaHei",valign:"middle"});
  s.addText("07  |  深度专题研究",{x:0.5,y:fy+0.01,w:W-1,h:0.3,fontSize:9,color:"94A3B8",fontFace:"Microsoft YaHei",align:"right",valign:"middle"});
}
function addCard(s,x,y,w,h,title,body,barColor){
  s.addShape(S.roundRect,{x,y,w,h,fill:{color:AC},line:{color:"E2E8F0",width:1},rectRadius:0.08});
  s.addShape(S.roundRect,{x,y,w,h:0.22,fill:{color:barColor},line:{color:barColor},rectRadius:0.08});
  s.addShape(S.rect,{x:x+0.02,y:y+0.15,w:w-0.04,h:0.1,fill:{color:AC},line:{color:AC}});
  s.addText(title,{x:x+0.2,y:y+0.26,w:w-0.4,h:0.4,fontSize:13,bold:true,color:T,fontFace:"Microsoft YaHei",valign:"middle"});
  if(body&&body.length>0){
    s.addText(body,{x:x+0.2,y:y+0.7,w:w-0.4,h:h-1.0,valign:"top",lineSpacingMultiple:1.15,fontSize:9.5,color:TL,fontFace:"Microsoft YaHei"});
  }
}
function statCard(s,x,y,w,num,label,color){
  s.addShape(S.roundRect,{x,y,w,h:1.05,fill:{color:color},line:{color:color},rectRadius:0.1});
  s.addText(num,{x,y:y+0.06,w,h:0.55,fontSize:24,bold:true,color:AC,fontFace:"Arial",align:"center",valign:"middle"});
  s.addText(label,{x,y:y+0.58,w,h:0.38,fontSize:9.5,color:AC,fontFace:"Microsoft YaHei",align:"center",valign:"middle"});
}
function drawRow(s,x,y,w,h,cells,cw,bg,isH){
  s.addShape(S.rect,{x,y,w,h,fill:{color:bg},line:{color:"E2E8F0",width:0.5}});
  var cx=x;
  cells.forEach(function(c,i){
    s.addText(c,{x:cx+0.05,y:y+0.04,w:cw[i]-0.1,h:h-0.08,fontSize:isH?10:9.5,bold:!!isH,color:isH?AC:T,fontFace:"Microsoft YaHei",align:i===0?"left":"center",valign:"middle"});
    cx+=cw[i];
  });
}

// ============================================================
// SLIDE 1: Chapter Cover
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s,P);
  s.addShape(S.ellipse,{x:-1.5,y:0.5,w:7,h:7,fill:{color:"1A3A6B",transparency:50}});
  s.addShape(S.ellipse,{x:9.5,y:-0.5,w:6,h:6,fill:{color:"1A3A6B",transparency:45}});
  s.addShape(S.ellipse,{x:5,y:4.5,w:4,h:4,fill:{color:"1E3A6E",transparency:40}});
  s.addText("07",{x:0.8,y:1.0,w:5,h:3,fontSize:100,bold:true,color:SC,fontFace:"Arial",valign:"middle",transparency:18});
  s.addShape(S.rect,{x:0.8,y:3.8,w:6,h:0.05,fill:{color:TE},line:{color:TE}});
  s.addText("深度专题研究",{x:0.8,y:3.9,w:12,h:1.2,fontSize:40,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addText("Deep Dive Research Topics  |  制造专用",{x:0.8,y:5.0,w:12,h:0.6,fontSize:16,color:SC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addShape(S.rect,{x:0.8,y:5.7,w:3,h:0.03,fill:{color:TL2},line:{color:TL2}});
  s.addText("变革管理  Change Management",{x:0.8,y:5.9,w:3.8,h:0.35,fontSize:11,color:TE,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addText("质量标准整合  Quality Standards Integration",{x:4.8,y:5.9,w:4.5,h:0.35,fontSize:11,color:G,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addText("精益数字化  Lean Digitalization",{x:9.5,y:5.9,w:3.8,h:0.35,fontSize:11,color:WA,fontFace:"Microsoft YaHei",valign:"middle"});
})();

// ============================================================
// SLIDE 2: Section Divider - 变革管理
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s,"0F172A");
  s.addShape(S.rect,{x:0,y:0,w:W,h:0.08,fill:{color:TE},line:{color:TE}});
  s.addText("SECTION  01",{x:0.8,y:1.2,w:12,h:0.6,fontSize:14,color:TE,fontFace:"Arial",valign:"middle"});
  s.addShape(S.rect,{x:0.8,y:1.85,w:0.8,h:0.45,fill:{color:TE},line:{color:TE}});
  s.addText("01",{x:0.8,y:1.85,w:0.8,h:0.45,fontSize:22,bold:true,color:AC,fontFace:"Arial",align:"center",valign:"middle"});
  s.addText("变革管理",{x:2.0,y:1.8,w:10,h:1.5,fontSize:52,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addText("Change Management  |  Leading Transformation in Manufacturing Plants",{x:0.8,y:3.4,w:12,h:0.6,fontSize:16,color:SC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addShape(S.rect,{x:0.8,y:4.2,w:4,h:0.04,fill:{color:TE},line:{color:TE}});
  s.addShape(S.rect,{x:0.8,y:4.6,w:0.1,h:0.38,fill:{color:TE},line:{color:TE}});
  s.addText("科特八步变革模型  —  Kotter's 8-Step Change Model",{x:1.1,y:4.6,w:10,h:0.4,fontSize:14,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addShape(S.rect,{x:0.8,y:5.2,w:0.1,h:0.38,fill:{color:TE},line:{color:TE}});
  s.addText("精益人才发展  —  Lean Talent Development & Competency Model",{x:1.1,y:5.2,w:10,h:0.4,fontSize:14,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
})();

// ============================================================
// SLIDE 3: Kotter's 8-Step Change Model
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,TE,0.06);
  addTitleBand(s,"科特八步变革模型","Kotter's 8-Step Change Model — Discrete Manufacturing Application");
  addFooter(s,"变革管理  |  Change Management");
  var steps=[
    {cn:"建立紧迫感",en:"Create Urgency",c:D,action:"展示交期延误、客户投诉、利润下降数据；对标行业最佳实践"},
    {cn:"组建领导联盟",en:"Form Coalition",c:"6B21A8",action:"生产/质量/工程/HR总监组成跨部门变革核心小组"},
    {cn:"构建战略愿景",en:"Build Vision",c:P,action:"定义精益工厂愿景：换型<5min，OEE>85%，零缺陷交货"},
    {cn:"沟通变革愿景",en:"Communicate Vision",c:"3B82F6",action:"全员大会、看板、班前会反复传递，用工件实物展示缺陷成本"},
    {cn:"授权行动",en:"Enable Action",c:WA,action:"消除障碍：老旧设备更新、作业员提案制度、跨车间改善团队"},
    {cn:"创造短期成果",en:"Quick Wins",c:G,action:"选定试点产线30天内OEE提升10%，可视化成果公开展示"},
    {cn:"巩固成果深化",en:"Consolidate",c:"0891B2",action:"推广至全厂，用数据证明效益，调整KPI体系对齐精益目标"},
    {cn:"文化融合",en:"Anchoring",c:TE,action:"将精益行为纳入晋升标准、新员工培训、年度表彰体系"}
  ];
  var gap2=0.1, colW=(W-0.5-gap2*3)/4, rowH=2.5;
  steps.forEach(function(st,i){
    var col=i%4, row=Math.floor(i/4);
    var bx=0.25+col*(colW+gap2), by=1.75+row*(rowH+gap2);
    s.addShape(S.roundRect,{x:bx,y:by,w:colW,h:rowH,fill:{color:st.c},line:{color:st.c},rectRadius:0.08});
    s.addShape(S.ellipse,{x:bx+0.1,y:by+0.1,w:0.38,h:0.38,fill:{color:"FFFFFF",transparency:25},line:{color:"FFFFFF",width:0.5}});
    s.addText(String(i+1),{x:bx+0.1,y:by+0.1,w:0.38,h:0.38,fontSize:12,bold:true,color:AC,fontFace:"Arial",align:"center",valign:"middle"});
    s.addText(st.cn,{x:bx+0.55,y:by+0.1,w:colW-0.65,h:0.34,fontSize:11,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
    s.addText(st.en,{x:bx+0.15,y:by+0.48,w:colW-0.3,h:0.2,fontSize:7.5,color:AC,fontFace:"Arial",transparency:55});
    s.addShape(S.rect,{x:bx+0.15,y:by+0.72,w:colW-0.3,h:0.02,fill:{color:"FFFFFF"},line:{color:"FFFFFF"},transparency:40});
    s.addText(st.action,{x:bx+0.15,y:by+0.8,w:colW-0.3,h:rowH-0.88,fontSize:8,color:AC,fontFace:"Microsoft YaHei",valign:"top",lineSpacingMultiple:1.18});
    if(col<3){
      s.addShape(S.rightArrow,{x:bx+colW+0.01,y:by+rowH/2-0.15,w:gap2-0.02,h:0.3,fill:{color:"CBD5E1"},line:{color:"CBD5E1"}});
    }
  });
})();

// ============================================================
// SLIDE 4: Lean Talent Development
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,TE,0.06);
  addTitleBand(s,"精益人才发展","Lean Talent Development — 4-Level Competency Model & Training Roadmap");
  addFooter(s,"变革管理  |  Change Management");
  var rtx=0.3, rty=1.75, rtw=3.2, rth=4.8;
  s.addShape(S.roundRect,{x:rtx,y:rty,w:rtw,h:rth,fill:{color:"EFF6FF"},line:{color:"BFDBFE"},rectRadius:0.08});
  s.addText("培训路线图",{x:rtx+0.2,y:rty+0.15,w:rtw-0.4,h:0.35,fontSize:12,bold:true,color:P,fontFace:"Microsoft YaHei"});
  s.addText("Training Roadmap",{x:rtx+0.2,y:rty+0.45,w:rtw-0.4,h:0.25,fontSize:8,color:P,fontFace:"Arial",transparency:50});
  var roadmap=[
    {t:"第1月",m:"精益基础培训",c:WA},
    {t:"第2-3月",m:"VSM / 5S实战",c:G},
    {t:"第4-6月",m:"标准化 / TPM",c:TE},
    {t:"第7-12月",m:"FMEA / APQP整合",c:P},
    {t:"第2年",m:"独立主导改善周",c:D}
  ];
  var ry=rty+0.85;
  roadmap.forEach(function(r){
    s.addShape(S.roundRect,{x:rtx+0.15,y:ry,w:0.65,h:0.28,fill:{color:r.c},line:{color:r.c},rectRadius:0.06});
    s.addText(r.t,{x:rtx+0.15,y:ry,w:0.65,h:0.28,fontSize:7.5,bold:true,color:AC,fontFace:"Microsoft YaHei",align:"center",valign:"middle"});
    s.addShape(S.rightArrow,{x:rtx+0.85,y:ry+0.1,w:0.2,h:0.12,fill:{color:"CBD5E1"},line:{color:"CBD5E1"}});
    s.addText(r.m,{x:rtx+1.1,y:ry,w:rtw-1.3,h:0.28,fontSize:9.5,color:P,fontFace:"Microsoft YaHei",valign:"middle"});
    ry+=0.65;
  });
  var lx=rtx+rtw+0.3, lw=8.8;
  var levels=[
    {cn:"认知级",en:"Awareness L1",c:WA,y:1.75,h:0.95,d:"理解精益基本概念；知道七种浪费类型；积极参与5S活动"},
    {cn:"实践者",en:"Practitioner L2",c:G,y:2.85,h:0.95,d:"掌握核心3工具 VSM/标准化/5S；日常运营中主动识别浪费并实施改善"},
    {cn:"专家级",en:"Expert L3",c:TE,y:3.95,h:0.95,d:"精通5+种精益工具；独立解决复杂交期/质量问题；主导跨部门改善周"},
    {cn:"教练级",en:"Coach L4",c:P,y:5.05,h:0.95,d:"独立主导精益转型项目；能做A3报告辅导、VSM分析指导；培训带领新人"}
  ];
  levels.forEach(function(lv){
    s.addShape(S.roundRect,{x:lx,y:lv.y,w:lw,h:lv.h,fill:{color:lv.c},line:{color:lv.c},rectRadius:0.08});
    s.addText(lv.cn,{x:lx+0.25,y:lv.y+0.06,w:3,h:0.36,fontSize:13,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
    s.addText(lv.en,{x:lx+lw-4,y:lv.y+0.12,w:3.6,h:0.26,fontSize:8.5,color:AC,fontFace:"Arial",align:"right",valign:"middle",transparency:55});
    s.addText(lv.d,{x:lx+0.25,y:lv.y+0.44,w:lw-0.5,h:0.46,fontSize:9.5,color:AC,fontFace:"Microsoft YaHei",valign:"top",lineSpacingMultiple:1.15});
  });
  s.addShape(S.roundRect,{x:lx,y:6.15,w:lw,h:0.55,fill:{color:"E0E7FF"},line:{color:"C7D2FE"},rectRadius:0.06});
  s.addText("精益晋升标准: 改善提案数 + 绿带/黄带认证 + 带教新人数 + OEE提升贡献量化",
    {x:lx+0.2,y:6.17,w:lw-0.4,h:0.5,fontSize:10.5,bold:true,color:P,fontFace:"Microsoft YaHei",align:"center",valign:"middle"});
})();

// ============================================================
// SLIDE 5: Section Divider - Quality Standards Integration
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s,"0F172A");
  s.addShape(S.rect,{x:0,y:0,w:W,h:0.08,fill:{color:G},line:{color:G}});
  s.addText("SECTION  02",{x:0.8,y:1.2,w:12,h:0.6,fontSize:14,color:G,fontFace:"Arial",valign:"middle"});
  s.addShape(S.rect,{x:0.8,y:1.85,w:0.8,h:0.45,fill:{color:G},line:{color:G}});
  s.addText("02",{x:0.8,y:1.85,w:0.8,h:0.45,fontSize:22,bold:true,color:AC,fontFace:"Arial",align:"center",valign:"middle"});
  s.addText("质量标准整合",{x:2.0,y:1.8,w:10,h:1.5,fontSize:52,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addText("Quality Standards Integration  |  IATF 16949 & CQI-9 for Manufacturings",{x:0.8,y:3.4,w:12,h:0.6,fontSize:16,color:SC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addShape(S.rect,{x:0.8,y:4.2,w:4,h:0.04,fill:{color:G},line:{color:G}});
  s.addShape(S.rect,{x:0.8,y:4.6,w:0.1,h:0.38,fill:{color:G},line:{color:G}});
  s.addText("IATF 16949与精益整合  —  IATF 16949 Mapped to Lean Tools",{x:1.1,y:4.6,w:10,h:0.4,fontSize:14,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addShape(S.rect,{x:0.8,y:5.2,w:0.1,h:0.38,fill:{color:G},line:{color:G}});
  s.addText("CQI-9热处理精益  —  CQI-9 Heat Treatment + TPM/Standard Work",{x:1.1,y:5.2,w:10,h:0.4,fontSize:14,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
})();

// ============================================================
// SLIDE 6: IATF 16949 and Lean Tool Mapping
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,G,0.06);
  addTitleBand(s,"IATF 16949与精益整合","IATF 16949 Requirements Mapped to Lean Tools — Dual Compliance");
  addFooter(s,"质量标准整合  |  Quality Standards Integration");
  var tw=W-1, th=0.42;
  var cw=[3.2,3.3,3.7];
  drawRow(s,0.5,1.75,tw,th,["IATF核心要求","对应精益工具","产品实施要点"],cw,P,true);
  var rows=[
    ["APQP 产品质量先期策划","VSM 价值流图","VSM分析从原材料到成品全过程，识别增值/非增值环节"],
    ["FMEA 潜在失效模式分析","Poka-Yoke 防错","在机加工/精加工/热处理工序设置防错装置，防止缺陷流出"],
    ["SPC 统计过程控制","标准作业 Standard Work","标准作业确保过程稳定性，SPC监控关键尺寸如关键直径"],
    ["MSA 测量系统分析","TPM 全面生产维护","测量设备TPM管理确保GRR<10%，保障检测数据可靠性"],
    ["PPAP 生产件批准程序","看板 Kanban","看板系统确保供应与节拍匹配，PPAP阶段的产能验证"]
  ];
  var cy=1.75+th;
  rows.forEach(function(r,i){
    drawRow(s,0.5,cy,tw,th,[r[0],r[1],r[2]],cw,i%2===0?AC:"F8FAFC",false);
    cy+=th;
  });
  cy+=0.2;
  var cards=[
    {t:"APQP x VSM",x:0.5,c:P,d:"产品策划阶段使用VSM设计未来状态工艺图，确保工艺路线最优"},
    {t:"FMEA x Poka-Yoke",x:4.75,c:TE,d:"高RPN工序优先部署防错，降低严重度和发生度，双重保障"},
    {t:"SPC x Std Work",x:9.0,c:WA,d:"标准作业保证过程一致性，SPC实时发现异常趋势并预警"}
  ];
  cards.forEach(function(card){
    s.addShape(S.roundRect,{x:card.x,y:cy,w:3.7,h:1.5,fill:{color:card.c},line:{color:card.c},rectRadius:0.08});
    s.addText(card.t,{x:card.x+0.15,y:cy+0.1,w:3.4,h:0.35,fontSize:12,bold:true,color:AC,fontFace:"Microsoft YaHei"});
    s.addText(card.d,{x:card.x+0.15,y:cy+0.5,w:3.4,h:0.9,fontSize:8.5,color:AC,fontFace:"Microsoft YaHei",lineSpacingMultiple:1.2,valign:"top"});
  });
})();

// ============================================================
// SLIDE 7: CQI-9 Heat Treatment Lean
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,G,0.06);
  addTitleBand(s,"CQI-9热处理精益","CQI-9 Heat Treatment Audit Integrated with TPM & Standard Work");
  addFooter(s,"质量标准整合  |  Quality Standards Integration");
  // CQI-9 core requirements card
  addCard(s,0.5,1.75,5.8,2.5,"CQI-9核心要求",[
    {text:"过程监控: 温度均匀性测试TUS、系统精度测试SAT"},
    {text:"炉温均匀性: 连续炉14C / 批式炉10C公差要求"},
    {text:"关键参数: 温度/时间/气氛/冷却速率/装炉方式"},
    {text:"控制计划: 热电偶布置、记录频率、报警限设定"},
    {text:"反应时间: 超出公差后必须在规定时间内处理"}
  ],G);
  // TPM + Standard Work integration
  addCard(s,6.8,1.75,6.0,2.5,"TPM x Standard Work 整合",[
    {text:"TPM自主维护: 操作员每日点检炉温仪表，确认正常范围",bold:false},
    {text:"Standard Work: 点检步骤标准化: 看仪表记录校验漏气"},
    {text:"PM计划: 每月热电偶校验，每季度TUS测试"},
    {text:"OEE追踪: 设备可用率x性能率x良品率综合评分"}
  ],TE);
  // Monitoring parameters
  s.addText("关键炉内监控参数",{x:0.5,y:4.4,w:8,h:0.3,fontSize:11,bold:true,color:G,fontFace:"Microsoft YaHei"});
  var params=[
    {name:"炉温均匀性",spec:"+-14C 连续炉",crit:"直接影响工件抗拉/硬度",c:G},
    {name:"保温时间",spec:"按材质计算",crit:"不足则组织转变不完全",c:P},
    {name:"碳势控制",spec:"0.75+-0.05 %C",crit:"影响表面碳含量与渗层",c:TE},
    {name:"冷却速率",spec:"C/s 按材料定",crit:"过快裂纹，过慢效率低",c:WA},
    {name:"热电偶寿命",spec:"6月更换",crit:"漂移致炉温失准批量风险",c:D}
  ];
  var pw=(W-1)/5, px2=0.5, py2=4.7;
  params.forEach(function(p,i){
    var bx=px2+i*pw;
    s.addShape(S.roundRect,{x:bx,y:py2,w:pw-0.1,h:2.2,fill:{color:p.c},line:{color:p.c},rectRadius:0.08});
    s.addText(p.name,{x:bx+0.12,y:py2+0.08,w:pw-0.34,h:0.32,fontSize:10,bold:true,color:AC,fontFace:"Microsoft YaHei",align:"center"});
    s.addText(p.spec,{x:bx+0.12,y:py2+0.45,w:pw-0.34,h:0.25,fontSize:8.5,color:AC,fontFace:"Arial",align:"center",transparency:70});
    s.addShape(S.rect,{x:bx+0.3,y:py2+0.76,w:pw-0.7,h:0.02,fill:{color:"FFFFFF"},line:{color:"FFFFFF"},transparency:40});
    s.addText(p.crit,{x:bx+0.12,y:py2+0.84,w:pw-0.34,h:1.2,fontSize:8,color:AC,fontFace:"Microsoft YaHei",align:"center",lineSpacingMultiple:1.2,valign:"top",wrap:true});
  });
})();

// ============================================================
// SLIDE 8: Section Divider - Lean Digitalization
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s,"0F172A");
  s.addShape(S.rect,{x:0,y:0,w:W,h:0.08,fill:{color:WA},line:{color:WA}});
  s.addText("SECTION  03",{x:0.8,y:1.2,w:12,h:0.6,fontSize:14,color:WA,fontFace:"Arial",valign:"middle"});
  s.addShape(S.rect,{x:0.8,y:1.85,w:0.8,h:0.45,fill:{color:WA},line:{color:WA}});
  s.addText("03",{x:0.8,y:1.85,w:0.8,h:0.45,fontSize:22,bold:true,color:AC,fontFace:"Arial",align:"center",valign:"middle"});
  s.addText("精益数字化",{x:2.0,y:1.8,w:10,h:1.5,fontSize:52,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addText("Lean Digitalization  |  Industry 4.0 for Discrete Manufacturing",{x:0.8,y:3.4,w:12,h:0.6,fontSize:16,color:SC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addShape(S.rect,{x:0.8,y:4.2,w:4,h:0.04,fill:{color:WA},line:{color:WA}});
  s.addShape(S.rect,{x:0.8,y:4.6,w:0.1,h:0.38,fill:{color:WA},line:{color:WA}});
  s.addText("精益数字化路线图  —  4-Phase Digital Transformation Roadmap",{x:1.1,y:4.6,w:10,h:0.4,fontSize:14,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  s.addShape(S.rect,{x:0.8,y:5.2,w:0.1,h:0.38,fill:{color:WA},line:{color:WA}});
  s.addText("IoT+TPM智能维护 & AI质量预测  —  Predictive Maintenance & AI Quality",{x:1.1,y:5.2,w:10,h:0.4,fontSize:14,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
})();

// ============================================================
// SLIDE 9: 4-Phase Digital Transformation Roadmap
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,WA,0.06);
  addTitleBand(s,"精益数字化路线图","4-Phase Digital Transformation — Digitize to Predict (24-Month Plan)");
  addFooter(s,"精益数字化  |  Lean Digitalization");
  var phases=[
    {cn:"数字化",en:"Digitize",cn2:"Phase 1",c:P,t:"0-6月",items:["纸质记录电子化","设备PLC数据采集","SPC系统上线","手持终端替代纸质作业单"],tech:"IoT传感器 MES基础 条形码RFID"},
    {cn:"连接",en:"Connect",cn2:"Phase 2",c:TE,t:"6-12月",items:["设备互联MQTT/OPC-UA","实时OEE看板","Andon系统数字化","VSM实时数据化"],tech:"工业网关 MQTT OPC-UA 云平台"},
    {cn:"分析",en:"Analyze",cn2:"Phase 3",c:"3B82F6",t:"12-18月",items:["大数据分析平台","异常自动预警","换型参数智能推荐","质量预测模型启动"],tech:"时序数据库 ML框架 BI看板"},
    {cn:"预测",en:"Predict",cn2:"Phase 4",c:G,t:"18-24月",items:["预测性维护系统","数字孪生工厂","自适应工艺参数优化","智能排产APS系统"],tech:"数字孪生 AI/ML APS 5G专网"}
  ];
  var pw3=(W-1)/4, gap3=0.12, px3=0.5, py3=1.75;
  phases.forEach(function(ph,i){
    var bx=px3+i*(pw3+gap3);
    s.addShape(S.roundRect,{x:bx,y:py3,w:pw3,h:1.5,fill:{color:ph.c},line:{color:ph.c},rectRadius:0.08});
    s.addText(ph.cn,{x:bx+0.12,y:py3+0.1,w:pw3-0.24,h:0.36,fontSize:13,bold:true,color:AC,fontFace:"Microsoft YaHei",align:"center"});
    s.addText(ph.cn2,{x:bx+0.12,y:py3+0.44,w:pw3-0.24,h:0.22,fontSize:8,color:AC,fontFace:"Arial",align:"center",transparency:60});
    s.addShape(S.roundRect,{x:bx+pw3/2-0.5,y:py3+0.68,w:1.0,h:0.32,fill:{color:"FFFFFF",transparency:30},line:{color:"FFFFFF",width:0.5},rectRadius:0.1});
    s.addText(ph.t,{x:bx+pw3/2-0.5,y:py3+0.68,w:1.0,h:0.32,fontSize:9,bold:true,color:AC,fontFace:"Arial",align:"center",valign:"middle"});
    s.addShape(S.rect,{x:bx+0.15,y:py3+1.05,w:pw3-0.3,h:0.02,fill:{color:"FFFFFF"},line:{color:"FFFFFF"},transparency:40});
    s.addText(ph.tech,{x:bx+0.12,y:py3+1.1,w:pw3-0.24,h:0.3,fontSize:7,color:AC,fontFace:"Arial",align:"center"});
    var iy=py3+1.55, iw=pw3-0.12, ix2=bx+0.06;
    ph.items.forEach(function(item,j){
      s.addShape(S.roundRect,{x:ix2,y:iy,w:iw,h:0.55,fill:{color:"EFF6FF"},line:{color:"DBEAFE"},rectRadius:0.05});
      s.addText(item,{x:ix2+0.12,y:iy+0.04,w:iw-0.24,h:0.47,fontSize:8.5,color:P,fontFace:"Microsoft YaHei",valign:"middle",lineSpacingMultiple:1.1});
      iy+=0.59;
    });
    if(i<3){
      s.addShape(S.rightArrow,{x:bx+pw3+0.01,y:py3+0.72,w:gap3-0.02,h:0.3,fill:{color:"CBD5E1"},line:{color:"CBD5E1"}});
    }
  });
  // Bottom summary box
  s.addShape(S.roundRect,{x:0.5,y:HT-0.9,w:W-1,h:0.5,fill:{color:"FFF7ED"},line:{color:"FED7AA"},rectRadius:0.06});
  s.addText("预期收益: 设备停机减少40% | 质量缺陷率降低35% | OEE提升15-20% | 换型时间降低50%",
    {x:0.7,y:HT-0.88,w:W-1.4,h:0.45,fontSize:11,bold:true,color:"9A3412",fontFace:"Microsoft YaHei",align:"center",valign:"middle"});
})();

// ============================================================
// SLIDE 10: IoT + TPM Smart Maintenance
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,WA,0.06);
  addTitleBand(s,"IoT+TPM智能维护","IoT Sensors for Predictive Maintenance & Digital Twin");
  addFooter(s,"精益数字化  |  Lean Digitalization");
  // Three sensor type cards
  var sensors=[
    {name:"振动监测",unit:"mm/s",c:D,items:["机加工设备轴承磨损预警","精加工设备刀具断裂检测","主电机不平衡监测","频谱偏差>20%触发报警"]},
    {name:"温度监测",unit:"C",c:WA,items:["炉温均匀性持续监控","轴承温度异常预警","电机绕组过热保护","温升>5C/小时触发报警"]},
    {name:"电流监测",unit:"A",c:TE,items:["机加工负载变化监测","空载能耗异常识别","刀具磨损间接判断","电流波动>15%触发报警"]}
  ];
  var sw4=(W-1.5)/3, sx4=0.5, sy4=1.75;
  sensors.forEach(function(sen,i){
    var bx=sx4+i*(sw4+0.25);
    s.addShape(S.roundRect,{x:bx,y:sy4,w:sw4,h:2.6,fill:{color:sen.c},line:{color:sen.c},rectRadius:0.08});
    s.addText(sen.name,{x:bx+0.15,y:sy4+0.1,w:sw4-0.3,h:0.36,fontSize:13,bold:true,color:AC,fontFace:"Microsoft YaHei",align:"center"});
    s.addText(sen.unit,{x:bx+0.15,y:sy4+0.46,w:sw4-0.3,h:0.22,fontSize:8,color:AC,fontFace:"Arial",align:"center",transparency:60});
    s.addShape(S.rect,{x:bx+0.2,y:sy4+0.72,w:sw4-0.4,h:0.02,fill:{color:"FFFFFF"},line:{color:"FFFFFF"},transparency:40});
    sen.items.forEach(function(it,j){
      s.addText(it,{x:bx+0.2,y:sy4+0.8+j*0.28,w:sw4-0.4,h:0.26,fontSize:9,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
    });
  });
  // Digital twin section
  s.addText("数字孪生四层架构",{x:0.5,y:4.5,w:8,h:0.3,fontSize:11,bold:true,color:WA,fontFace:"Microsoft YaHei"});
  var dt=[
    {t:"物理层 Physical",x:0.5,w:2.8,c:P,d:"机加工设备/精加工设备/热处理炉 + IoT传感器实时采集"},
    {t:"数据层 Data",x:3.7,w:2.8,c:TE,d:"边缘计算网关到云端时序数据库，清洗+聚合"},
    {t:"模型层 Model",x:6.9,w:2.8,c:"3B82F6",d:"3D物理仿真 + 退化模型 + 异常检测算法"},
    {t:"应用层 Apply",x:10.1,w:2.6,c:G,d:"预测性维护决策、远程监控、工艺参数优化"}
  ];
  dt.forEach(function(d,i){
    s.addShape(S.roundRect,{x:d.x,y:4.9,w:d.w,h:1.35,fill:{color:d.c},line:{color:d.c},rectRadius:0.08});
    s.addText(d.t,{x:d.x+0.12,y:4.96,w:d.w-0.24,h:0.32,fontSize:10,bold:true,color:AC,fontFace:"Microsoft YaHei",align:"center"});
    s.addText(d.d,{x:d.x+0.12,y:5.3,w:d.w-0.24,h:0.95,fontSize:8.5,color:AC,fontFace:"Microsoft YaHei",lineSpacingMultiple:1.15,valign:"top",wrap:true});
    if(i<3){
      s.addShape(S.rightArrow,{x:d.x+d.w+0.04,y:5.55-0.15,w:0.17,h:0.3,fill:{color:"CBD5E1"},line:{color:"CBD5E1"}});
    }
  });
  // ROI stat cards
  statCard(s,0.5,6.4,1.2,"50%","故障减少",G);
  statCard(s,1.9,6.4,1.2,"30%","维修成本降低",TE);
  statCard(s,3.3,6.4,1.2,"2x","设备寿命延长",P);
  statCard(s,4.7,6.4,1.3,"2.5x","投资回报率",WA);
})();

// ============================================================
// SLIDE 11: AI Quality Prediction
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s); addTopBar(s,WA,0.06);
  addTitleBand(s,"AI质量预测","AI/ML for Quality Prediction in Discrete Manufacturing");
  addFooter(s,"精益数字化  |  Lean Digitalization");
  var apps=[
    {t:"缺陷预测模型",st:"Defect Prediction",c:P,
      items:["输入: 温度/压力/速度/时间/材质批号","模型: XGBoost + 随机森林集成","输出: 缺陷概率预测 + 关键因子排名","应用: 机加工裂纹预测、加工不完整预警"]},
    {t:"智能SPC",st:"AI-Enhanced SPC",c:TE,
      items:["传统SPC: 事后发现、批量报废风险","AI-SPC: 趋势预测、提前调整、防患未然","模式识别: 自动分类普通/特殊原因变异","应用: 关键尺寸趋势预测、硬度分布预警"]},
    {t:"自动视觉检测",st:"Automated Visual Insp.",c:WA,
      items:["技术: 深度学习CNN + 工业相机","检测项: 表面裂纹/端部变形/加工缺损","速度: >600件/分钟，超越人工检测极限","准确率: >99.5%，持续学习迭代优化"]}
  ];
  var aw5=(W-1.5)/3, ax5=0.5, ay5=1.75;
  apps.forEach(function(app,i){
    var bx=ax5+i*(aw5+0.25);
    s.addShape(S.roundRect,{x:bx,y:ay5,w:aw5,h:4.6,fill:{color:app.c},line:{color:app.c},rectRadius:0.08});
    s.addText(app.t,{x:bx+0.15,y:ay5+0.12,w:aw5-0.3,h:0.36,fontSize:12,bold:true,color:AC,fontFace:"Microsoft YaHei",align:"center"});
    s.addText(app.st,{x:bx+0.15,y:ay5+0.46,w:aw5-0.3,h:0.22,fontSize:7.5,color:AC,fontFace:"Arial",align:"center",transparency:60});
    s.addShape(S.rect,{x:bx+0.2,y:ay5+0.72,w:aw5-0.4,h:0.02,fill:{color:"FFFFFF"},line:{color:"FFFFFF"},transparency:40});
    var ty=ay5+0.82;
    app.items.forEach(function(item,j){
      s.addShape(S.roundRect,{x:bx+0.15,y:ty,w:aw5-0.3,h:0.52,fill:{color:"FFFFFF",transparency:15},line:{color:"FFFFFF",width:0.3},rectRadius:0.05});
      s.addText(item,{x:bx+0.25,y:ty+0.04,w:aw5-0.5,h:0.44,fontSize:9,color:AC,fontFace:"Microsoft YaHei",valign:"middle",lineSpacingMultiple:1.1});
      ty+=0.58;
    });
  });
  // Summary insight
  s.addShape(S.roundRect,{x:0.5,y:HT-0.8,w:W-1,h:0.45,fill:{color:"FFF7ED"},line:{color:"FED7AA"},rectRadius:0.06});
  s.addText("核心理念: 从事后检验转向事前预测，从接受缺陷率迈向零缺陷制造",
    {x:0.7,y:HT-0.78,w:W-1.4,h:0.4,fontSize:11,bold:true,color:"9A3412",fontFace:"Microsoft YaHei",align:"center",valign:"middle"});
})();

// ============================================================
// SLIDE 12: Summary
// ============================================================
(function(){
  var s=pptx.addSlide(); setBg(s,"0F172A");
  s.addShape(S.rect,{x:0,y:0,w:W,h:0.08,fill:{color:TE},line:{color:TE}});
  s.addText("07",{x:0.5,y:0.4,w:3,h:2.5,fontSize:72,bold:true,color:SC,fontFace:"Arial",valign:"middle",transparency:20});
  s.addText("总结  |  Summary",{x:4.0,y:0.5,w:8,h:0.5,fontSize:24,bold:true,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
  var summaries=[
    {t:"变革管理",st:"Change Management",c:TE,
      items:["科特八步模型提供系统化变革路线图","从紧迫感到文化融合，避免变革逆转","4级人才发展路径支撑能力提升","精益晋升标准促进持续改善文化"]},
    {t:"质量标准整合",st:"Quality Integration",c:G,
      items:["IATF 16949与精益工具一一对应","APQP→VSM, FMEA→Poka-Yoke, SPC→Std Work","CQI-9热处理TPM点检标准化","质量内建: 检验转向过程保障"]},
    {t:"精益数字化",st:"Lean Digitalization",c:WA,
      items:["4阶段路线图: Digitize→Connect→Analyze→Predict","IoT传感器实现预测性维护，ROI达2.5倍","AI质量预测从事后检验转向事前预防","数字孪生工厂是终极目标"]}
  ];
  var sw6=(W-1.5)/3, sx6=0.5;
  summaries.forEach(function(sum,i){
    var bx=sx6+i*(sw6+0.25);
    s.addShape(S.roundRect,{x:bx,y:1.3,w:sw6,h:4.8,fill:{color:sum.c},line:{color:sum.c},rectRadius:0.08});
    s.addText(sum.t,{x:bx+0.15,y:1.42,w:sw6-0.3,h:0.38,fontSize:14,bold:true,color:AC,fontFace:"Microsoft YaHei",align:"center"});
    s.addText(sum.st,{x:bx+0.15,y:1.78,w:sw6-0.3,h:0.24,fontSize:8,color:AC,fontFace:"Arial",align:"center",transparency:60});
    s.addShape(S.rect,{x:bx+0.25,y:2.08,w:sw6-0.5,h:0.02,fill:{color:"FFFFFF"},line:{color:"FFFFFF"},transparency:40});
    sum.items.forEach(function(it,j){
      s.addText(it,{x:bx+0.2,y:2.2+j*0.65,w:sw6-0.4,h:0.55,fontSize:9.5,color:AC,fontFace:"Microsoft YaHei",valign:"middle"});
    });
  });
  s.addShape(S.rect,{x:0,y:HT-0.6,w:W,h:0.6,fill:{color:"0F172A"},line:{color:"0F172A"}});
  s.addText("变革引领方向 质量筑牢根基 数字铸就未来  |  Change x Quality x Digital = 精益卓越",
    {x:1,y:HT-0.55,w:W-2,h:0.45,fontSize:12,color:TE,fontFace:"Microsoft YaHei",align:"center",valign:"middle",bold:true});
})();

// ===== Generate =====
pptx.writeFile({ fileName: path.join(OUT, "07-深度专题研究.pptx") }).then(function(r){
  console.log("Done:", r);
}).catch(function(e){ console.error("Error:", e); process.exit(1); });
