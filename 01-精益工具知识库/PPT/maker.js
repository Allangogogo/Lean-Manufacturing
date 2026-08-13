// 精益工具知识库 PPT 生成器
// 执行: node maker.js
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const OUT = __dirname;
const C = { P:"1E2761", S:"CADCFC", A:"FFFFFF", L:"F8FAFC", T:"1E293B", TL:"64748B", G:"059669", W:"D97706", D:"DC2626", TE:"0D9488", TL2:"5EEAD4" };

function mk(title, slides, filename) {
  let p = new pptxgen(); p.layout = 'LAYOUT_16x9'; p.title = title;
  slides(p); p.writeFile({ fileName: path.join(OUT, filename) });
  console.log("✅ " + filename);
}

function hdr(p, title, sub) {
  let s = p.addSlide(); s.background = { color: C.L };
  s.addShape(p.shapes.RECTANGLE, { x:0, y:0, w:10, h:0.08, fill:{color:C.TE} });
  s.addShape(p.shapes.RECTANGLE, { x:0, y:0.08, w:10, h:0.75, fill:{color:C.P} });
  s.addText(title, { x:0.8, y:0.12, w:8.4, h:0.55, fontSize:26, fontFace:"Arial Black", color:C.A, bold:true, margin:0 });
  if(sub) s.addText(sub, { x:0.8, y:0.55, w:8.4, h:0.25, fontSize:13, fontFace:"Arial", color:C.S, margin:0 });
  return s;
}

function darkCover(p, num, title, sub, tagline) {
  let s = p.addSlide(); s.background = { color: C.P };
  s.addShape(p.shapes.RECTANGLE, { x:0, y:0, w:10, h:0.12, fill:{color:C.TE} });
  s.addShape(p.shapes.RECTANGLE, { x:8.5, y:0, w:1.5, h:5.625, fill:{color:"0F172A", transparency:30} });
  s.addText(num, { x:0.8, y:0.6, w:2, h:1, fontSize:72, fontFace:"Arial Black", color:C.TL2, bold:true });
  s.addText(title, { x:0.8, y:2.0, w:8, h:0.8, fontSize:36, fontFace:"Arial Black", color:C.A, bold:true });
  s.addText(sub, { x:0.8, y:2.9, w:8, h:0.5, fontSize:18, fontFace:"Arial", color:C.S });
  s.addShape(p.shapes.LINE, { x:0.8, y:3.6, w:3, h:0, line:{color:C.TE, width:3} });
  s.addText(tagline, { x:0.8, y=4.2, w:8, h:0.4, fontSize:12, fontFace:"Arial", color:C.S });
  return s;
}

function sc(s, x, y, num, label, color) {
  s.addShape(p.shapes.RECTANGLE, { x, y, w:2.2, h:1.2, fill:{color:"FFFFFF"}, shadow:{type:"outer",color:"000000",blur:6,offset:2,angle:135,opacity:0.1} });
  s.addShape(p.shapes.RECTANGLE, { x, y, w:0.08, h:1.2, fill:{color} });
  s.addText(num, { x:x+0.2, y:y+0.15, w:1.9, h:0.5, fontSize:26, fontFace:"Arial Black", color:C.P, bold:true, align:"center" });
  s.addText(label, { x:x+0.15, y:y+0.7, w:1.9, h:0.35, fontSize:8.5, fontFace:"Arial", color:C.TL, align:"center" });
}

function kpiTable(s, x, y, rows) {
  rows.forEach((row,ri)=>{
    row.forEach((cell,ci)=>{
      let cx=x+ci*2, cy=y+ri*0.34;
      let bg=ri===0?C.P:(ri%2===0?"FFFFFF":C.L);
      s.addShape(p.shapes.RECTANGLE, { x:cx, y:cy, w:1.95, h:0.32, fill:{color:bg} });
      s.addText(cell, { x:cx+0.05, y:cy+0.03, w:1.85, h:0.26, fontSize:8.5, fontFace:ri===0?"Arial Black":"Arial", color:ri===0?C.A:C.T, align:"center", valign:"middle", margin:0 });
    });
  });
}

// ============================================================
// PPT 1: 封面与目录
// ============================================================
mk("精益工具知识库 - 封面与目录", function(p) {
  // 封面
  let s = p.addSlide(); s.background = { color: C.P };
  s.addShape(p.shapes.RECTANGLE, { x:0, y:0, w:10, h:0.12, fill:{color:C.TE} });
  s.addShape(p.shapes.RECTANGLE, { x:8.5, y:0, w:1.5, h:5.625, fill:{color:"0F172A", transparency:30} });
  s.addText("精益工具知识库", { x:0.8, y:1.2, w:7.5, h:1.2, fontSize:44, fontFace:"Arial Black", color:C.A, bold:true });
  s.addText("金属紧固件制造企业精益转型核心指南", { x:0.8, y:2.5, w:7, h:0.6, fontSize:20, fontFace:"Arial", color:C.S });
  s.addShape(p.shapes.LINE, { x:0.8, y:3.3, w:3, h:0, line:{color:C.TE, width:3} });
  const cs = [{n:"13+",l:"核心精益工具"},{n:"5",l:"问题解决方法"},{n:"4",l:"深度专题"},{n:"70%",l:"转型失败率*"}];
  cs.forEach((c,i)=>{ sc(s, 0.8+i*2.2, 3.8, c.n, c.l, [C.TE,C.G,C.W,C.D][i]); });
  s.addText("* 精益转型失败率高达70%，根本原因在于变革管理而非工具技术", { x:0.8, y:5.1, w:8, h:0.3, fontSize:9, fontFace:"Arial", color:C.TL });

  // 目录
  s = hdr(p, "知识库目录", "Contents");
  const items = [
    {n:"01",t:"精益基础",d:"精益哲学 · 八大浪费 · TPS体系 · 术语表",c:C.P},
    {n:"02",t:"核心工具（13+）",d:"看板 · VSM · 安灯 · TPM · 5S · 改善 · 防错 · SMED 等",c:C.TE},
    {n:"03",t:"问题解决方法",d:"Gemba Walk · A3 · PDCA · DMAIC · VA/VE",c:C.G},
    {n:"04",t:"紧固件行业应用",d:"冷镦 · 搓丝 · 热处理 · 表面处理 · 包装",c:C.W},
    {n:"05",t:"实践案例集",d:"SMED改善案例 · 改善提案模板 · 实施指南",c:C.D},
    {n:"06",t:"深度专题研究",d:"变革管理 · VSM高级实战 · 质量标准整合 · 精益数字化",c:C.P},
  ];
  items.forEach((it,i)=>{
    let col=i%2, row=Math.floor(i/2);
    let x=0.5+col*4.7, y=1.2+row*1.3;
    s.addShape(p.shapes.RECTANGLE, { x, y, w:4.4, h:1.15, fill:{color:"FFFFFF"}, shadow:{type:"outer",color:"000000",blur:4,offset:1,angle:135,opacity:0.08} });
    s.addShape(p.shapes.RECTANGLE, { x, y, w:0.1, h:1.15, fill:{color:it.c} });
    s.addText(it.n, { x:x+0.2, y:y+0.08, w:0.6, h:0.35, fontSize:16, fontFace:"Arial Black", color:it.c, bold:true });
    s.addText(it.t, { x:x+0.8, y:y+0.1, w:3.3, h:0.3, fontSize:13, fontFace:"Arial Black", color:C.T, bold:true, margin:0 });
    s.addText(it.d, { x:x+0.2, y:y+0.45, w:4, h:0.5, fontSize:8.5, fontFace:"Arial", color:C.TL });
  });

  // 精益五大原则
  s = hdr(p, "精益五大原则", "Lean 5 Principles");
  const principles = [{n:"价值 Value",d:"从客户视角定义价值",g:"◎"},{n:"价值流 Value Stream",d:"识别端到端价值流",g:"⇒"},{n:"流动 Flow",d:"让价值持续流动",g:"▶"},{n:"拉动 Pull",d:"由需求驱动生产",g:"◀"},{n:"尽善尽美 Perfection",d:"追求永无止境的改进",g:"∞"}];
  principles.forEach((pr,i)=>{
    let x=0.5+i*1.9;
    s.addShape(p.shapes.OVAL, { x:x+0.3, y:1.3, w:1.2, h:1.2, fill:{color:C.P} });
    s.addText(pr.g, { x:x+0.3, y:1.45, w:1.2, h:0.6, fontSize:28, fontFace:"Arial", color:C.A, align:"center", valign:"middle" });
    s.addText(pr.n, { x:x, y:2.6, w:1.8, h:0.35, fontSize:10, fontFace:"Arial Black", color:C.T, align:"center", bold:true });
    s.addText(pr.d, { x:x, y:2.95, w:1.8, h:0.3, fontSize:8, fontFace:"Arial", color:C.TL, align:"center" });
  });
  s.addShape(p.shapes.RECTANGLE, { x:0.5, y:3.6, w:9, h:1.6, fill:{color:C.P, transparency:5} });
  s.addText("核心理念：消除浪费 · 尊重人性 · 持续改善 · 现地现物 · 长期思维", { x:0.8, y:3.75, w:8.4, h:0.4, fontSize:14, fontFace:"Arial Black", color:C.P, bold:true, align:"center" });

  // 八大浪费
  s = hdr(p, "八大浪费识别指南", "8 Wastes (Muda)");
  const wastes = [{n:"过量生产",e:"Overproduction",d:"超出需求的生产",p:"35%",c:C.D},{n:"等待",e:"Waiting",d:"人员/设备空闲",p:"20%",c:C.W},{n:"搬运",e:"Transportation",d:"不必要的物料移动",p:"10%",c:C.W},{n:"过度加工",e:"Over-processing",d:"超出客户要求的加工",p:"8%",c:C.TE},{n:"库存",e:"Inventory",d:"过量原材料/WIP/成品",p:"15%",c:C.P},{n:"动作",e:"Motion",d:"人员不必要的动作",p:"5%",c:C.TE},{n:"不良品",e:"Defects",d:"不合格品和返工",p:"5%",c:C.D},{n:"未利用人才",e:"Unused Talent",d:"员工智慧未被发挥",p:"2%",c:C.G}];
  wastes.forEach((w,i)=>{
    let col=i%4, row=Math.floor(i/4);
    let x=0.4+col*2.4, y=1.2+row*1.85;
    s.addShape(p.shapes.RECTANGLE, { x, y, w:2.2, h:1.65, fill:{color:"FFFFFF"}, shadow:{type:"outer",color:"000000",blur:3,offset:1,angle:135,opacity:0.06} });
    s.addShape(p.shapes.RECTANGLE, { x, y, w:2.2, h:0.24, fill:{color:w.c} });
    s.addText(w.n, { x:x+0.1, y:y+0.02, w:1.4, h:0.22, fontSize:10, fontFace:"Arial Black", color:C.A, bold:true, align:"center", margin:0 });
    s.addText(w.e, { x:x+1.5, y:y+0.04, w:0.6, h:0.18, fontSize:7, fontFace:"Arial", color:C.A, align:"center", margin:0 });
    s.addText(w.d, { x:x+0.1, y:y+0.3, w:2, h:0.22, fontSize:8, fontFace:"Arial", color:C.TL, align:"center", margin:0 });
    s.addText(w.p, { x:x+0.1, y:y+0.6, w:2, h:0.4, fontSize:24, fontFace:"Arial Black", color:w.c, bold:true, align:"center" });
  });
}, "01-封面与目录.pptx");

// ============================================================
// PPT 2: TPM与OEE详解
// ============================================================
mk("TPM与OEE详解", function(p) {
  darkCover(p,"01","TPM 与 OEE","全面生产维护 · 设备综合效率","全员参与的设备管理体系 | OEE = 可用率 × 性能率 × 合格率 | 世界级目标 >85%");

  // OEE计算
  let s = hdr(p, "OEE 计算详解", "Overall Equipment Effectiveness");
  s.addShape(p.shapes.RECTANGLE, { x:1.5, y:1.2, w:7, h:0.65, fill:{color:C.P, transparency:10}, rectRadius:0.1 });
  s.addText("OEE = 可用率 × 性能率 × 合格率", { x:1.5, y=1.25, w:7, h:0.55, fontSize:22, fontFace:"Arial Black", color:C.P, align:"center", valign:"middle" });
  const fcts = [{n:"可用率 Availability",f:"(计划时间-停机)/计划时间",t:">90%",e:"故障15min+换型10min+等待5min\n可用率=(440-30)/440=93.2%",c:C.TE},{n:"性能率 Performance",f:"理想节拍×产出/运行时间",t:">95%",e:"理想节拍1.0s，产出35000件\n性能率=35000/24600=87.5%",c:C.W},{n:"合格率 Quality",f:"合格品/总产出",t:">99.9%",e:"总产出35000，不良350，废品100\n合格率=34550/35000=98.7%",c:C.G}];
  fcts.forEach((f,i)=>{
    let x=0.4+i*3.2;
    s.addShape(p.shapes.RECTANGLE, { x, y:2.05, w:3, h:2.5, fill:{color:"FFFFFF"}, shadow:{type:"outer",color:"000000",blur:4,offset:1,angle:135,opacity:0.08} });
    s.addShape(p.shapes.RECTANGLE, { x, y:2.05, w:3, h:0.26, fill:{color:f.c} });
    s.addText(f.n, { x:x+0.1, y:2.07, w:2.8, h:0.23, fontSize:9, fontFace:"Arial Black", color:C.A, bold:true, align:"center", margin:0 });
    s.addText(f.f, { x:x+0.1, y:2.38, w:2.8, h=0.32, fontSize:8, fontFace:"Arial", color:C.T, align:"center" });
    s.addText("目标: "+f.t, { x:x+0.1, y:2.72, w:2.8, h=0.2, fontSize:8, fontFace:"Arial", color:f.c, align:"center", bold:true });
    s.addText(f.e, { x:x+0.1, y:2.98, w:2.8, h=1.4, fontSize:7, fontFace:"Arial", color:C.TL });
  });
  s.addText("综合 OEE = 93.2% × 87.5% × 98.7% = 80.3%", { x:1.5, y:4.7, w:7, h:0.35, fontSize:15, fontFace:"Arial Black", color:C.P, align:"center" });

  // 六大损失
  s = hdr(p, "OEE 六大损失分析", "Six Big Losses");
  const losses = [{n:"设备故障",c:"可用率",t:"45min",p:"32%",col:C.D},{n:"换型调整",c:"可用率",t:"35min",p:"25%",col:C.W},{n:"空转短停",c:"性能率",t:"18min",p:"13%",col:C.W},{n:"速度降低",c:"性能率",t:"20min",p:"14%",col:C.TE},{n:"过程缺陷",c:"合格率",t:"12min",p:"9%",col:C.D},{n:"开机废品",c:"合格率",t:"5min",p:"4%",col:C.TE}];
  losses.forEach((l,i)=>{
    let col=i%3, row=Math.floor(i/3), x=0.4+col*3.2, y=1.2+row*1.8;
    s.addShape(p.shapes.RECTANGLE, { x, y, w:3, h:1.6, fill:{color:"FFFFFF"}, shadow:{type:"outer",color:"000000",blur:3,offset:1,angle:135,opacity:0.06} });
    s.addShape(p.shapes.RECTANGLE, { x, y, w:3, h:0.22, fill:{color:l.col} });
    s.addText(l.n, { x:x+0.1, y:y+0.02, w:2.8, h:0.2, fontSize:11, fontFace:"Arial Black", color:C.A, bold:true, align:"center", margin:0 });
    s.addText("影响: "+l.c+"  |  损失: "+l.t, { x:x+0.1, y:y+0.28, w=2.8, h:0.2, fontSize:8, fontFace:"Arial", color:C.TL, align:"center", margin:0 });
    s.addText(l.p, { x:x+2, y:y+0.5, w=0.9, h=0.4, fontSize:24, fontFace:"Arial Black", color:l.col, bold:true, align:"center" });
  });

  // TPM八大支柱
  s = hdr(p, "TPM 八大支柱", "8 Pillars of TPM");
  const pillars = [{n:"自主维护",d:"操作员日常保养清扫点检",c:C.TE},{n:"计划维护",d:"预防性/预测性维护体系",c:C.P},{n:"个别改善",d:"设备损失专项改善攻关",c:C.W},{n:"教育训练",d:"维护技能体系化培训",c:C.G},{n:"初期管理",d:"新设备快速稳定投产",c:C.TE},{n:"品质维护",d:"设备精度保障与提升",c:C.D},{n:"事务改善",d:"办公流程精益化",c:C.P},{n:"安全环境",d:"零灾害零公害目标",c:C.G}];
  pillars.forEach((pl,i)=>{
    let col=i%4, row=Math.floor(i/4), x=0.4+col*2.4, y=1.2+row*1.7;
    s.addShape(p.shapes.RECTANGLE, { x, y, w:2.2, h:1.5, fill:{color:"FFFFFF"}, shadow:{type:"outer",color:"000000",blur:3,offset:1,angle:135,opacity:0.06} });
    s.addShape(p.shapes.RECTANGLE, { x, y, w:2.2, h:0.22, fill:{color:pl.c} });
    s.addText(pl.n, { x:x+0.1, y:y+0.02, w:2, h=0.2, fontSize:11, fontFace:"Arial Black", color:C.A, bold:true, align:"center", margin:0 });
    s.addText(pl.d, { x:x+0.1, y:y+0.28, w=2, h:0.2, fontSize:7.5, fontFace:"Arial", color:C.TL, align:"center", margin:0 });
  });

  // 自主维护七步法
  s = hdr(p, "自主维护七步法", "7 Steps of Autonomous Maintenance");
  const steps = ["1\n初期清扫","2\n发生源对策","3\n临时基准","4\n总点检","5\n自主点检","6\n标准化","7\n持续改善"];
  steps.forEach((st,i)=>{
    let x=0.5+i*1.3;
    s.addShape(p.shapes.RECTANGLE, { x, y:1.35, w:1.15, h:0.5, fill:{color:C.TE}, rectRadius:0.08 });
    s.addText(st, { x, y:1.37, w=1.15, h:0.45, fontSize:8.5, fontFace:"Arial Black", color:C.A, bold:true, align:"center", valign:"middle" });
    if(i<6) s.addText("→", { x:x+1.18, y:1.45, w:0.1, h=0.3, fontSize:12, fontFace:"Arial", color:C.TL, align:"center" });
  });
  s.addShape(p.shapes.RECTANGLE, { x:0.5, y:2.4, w:9, h=2.5, fill:{color:C.P, transparency:5} });
  s.addText("微缺陷放大效应", { x:0.8, y:2.5, w:4, h=0.35, fontSize:14, fontFace:"Arial Black", color:C.P, bold:true });
  const df = ["1个微缺陷","10个→1个中缺陷","10个→1个大缺陷","10个→1次故障","10个→1次重大事故"];
  df.forEach((d,i)=>{
    let dx=0.8+i*1.7;
    s.addShape(p.shapes.RECTANGLE, { x:dx, y:2.95, w=1.5, h=0.4, fill:{color:i===4?C.D:C.TE}, rectRadius:0.05 });
    s.addText(d, { x:dx, y:2.98, w=1.5, h=0.35, fontSize:7.5, fontFace:"Arial", color:C.A, align:"center", valign:"middle", bold:true });
    if(i<4) s.addText("→", { x:dx+1.55, y:3.0, w=0.12, h=0.35, fontSize:12, fontFace:"Arial", color:C.TL, align:"center" });
  });
  s.addText("1个重大事故背后可能有 1000 个微缺陷！", { x:0.8, y:3.75, w=8, h=0.35, fontSize:12, fontFace:"Arial Black", color:C.D, align:"center" });

  // OEE行业基准
  s = hdr(p, "OEE 行业基准与紧固件KPI", "OEE Benchmarks & Fastener KPI");
  sc(s, 0.5, 1.2, ">90%", "世界级 World Class", C.G);
  sc(s, 2.9, 1.2, "80-90%", "优秀 Excellent", C.TE);
  sc(s, 5.3, 1.2, "65-80%", "发展中 Developing", C.W);
