// 02 - TPM与OEE详解
const PptxGenJS = require("pptxgenjs");
const path = require("path");
const OUT = __dirname;

const C = { P:"1E2761", S:"CADCFC", A:"FFFFFF", L:"F8FAFC", T:"1E293B", TL:"64748B", G:"059669", W:"D97706", D:"DC2626", TE:"0D9488", TL2:"5EEAD4" };
const W = 13.33, H = 7.5;

let pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE"; pptx.title = "TPM与OEE详解"; pptx.author = "精益工具知识库";
const S = pptx.ShapeType;

function addTopBar(slide, color, barH) {
  slide.addShape(S.rect, { x:0, y:0, w:W, h:barH||0.08, fill:{color}, line:{color,width:0} });
}
function addTitleBand(slide, title, subtitle) {
  slide.addShape(S.rect, { x:0, y:0.08, w:W, h:0.92, fill:{color:C.P}, line:{color:C.P,width:0} });
  slide.addText(title, { x:0.5, y:0.12, w:W-1, h:0.52, fontFace:"Arial Black", fontSize:28, color:C.A, bold:true, valign:"middle" });
  if(subtitle) slide.addText(subtitle, { x:0.5, y:0.54, w:W-1, h:0.35, fontFace:"Arial", fontSize:14, color:C.S, valign:"middle" });
}
function setBg(slide) {
  slide.addShape(S.rect, { x:0, y:0.08, w:W, h:H-0.08, fill:{color:C.L}, line:{color:C.L,width:0} });
}
function addFooter(slide, text) {
  slide.addShape(S.rect, { x:0, y:H-0.32, w:W, h:0.32, fill:{color:C.P}, line:{color:C.P,width:0} });
  slide.addText(text, { x:0, y:H-0.32, w:W, h:0.32, fontFace:"Arial", fontSize:11, color:C.S, align:"center", valign:"middle" });
}
function statCard(slide, x, y, num, label, color, sub) {
  slide.addShape(S.roundRect, { x, y, w:2.8, h:1.5, fill:{color:C.A}, transparency:10, line:{color, width:1}, rectRadius:0.08 });
  slide.addShape(S.rect, { x, y, w:2.8, h:0.06, fill:{color}, line:{color,width:0} });
  slide.addText(num, { x, y:0.15, w:2.8, h:0.6, fontFace:"Arial Black", fontSize:28, color:C.A, align:"center", bold:true, valign:"middle" });
  slide.addText(label, { x, y:0.75, w:2.8, h:0.35, fontFace:"Arial", fontSize:11, color:C.S, align:"center", valign:"middle" });
  if(sub) slide.addText(sub, { x, y:1.05, w:2.8, h:0.35, fontFace:"Arial", fontSize:9, color:C.TL, align:"center", valign:"middle" });
}

// Slide 1: Dark Cover
let s1 = pptx.addSlide();
s1.addShape(S.rect, { x:0, y:0, w:W, h:H, fill:{color:C.P}, line:{color:C.P,width:0} });
addTopBar(s1, C.TE, 0.12);
s1.addShape(S.rect, { x:10.5, y:0, w:2.83, h:H, fill:{color:"0F172A"}, transparency:70, line:{color:"0F172A",width:0} });
s1.addShape(S.ellipse, { x:11.0, y:1.0, w:2.0, h:2.0, fill:{color:C.TE}, transparency:80, line:{color:C.TE,width:0} });
s1.addShape(S.ellipse, { x:11.5, y:3.0, w:1.5, h:1.5, fill:{color:C.A}, transparency:85, line:{color:C.A,width:0} });
s1.addText("02", { x:0.8, y:0.8, w:3, h:1.2, fontSize:80, fontFace:"Arial Black", color:C.TL2, bold:true });
s1.addText("TPM 与 OEE", { x:0.8, y:2.2, w:9, h:0.9, fontSize:40, fontFace:"Arial Black", color:C.A, bold:true });
s1.addText("全面生产维护 · 设备综合效率", { x:0.8, y:3.2, w:9, h:0.5, fontSize:18, fontFace:"Arial", color:C.S });
s1.addShape(S.rect, { x:0.8, y:3.9, w:3, h:0.05, fill:{color:C.TE}, line:{color:C.TE,width:0} });
s1.addText("全员参与的设备管理体系 | OEE = 可用率 × 性能率 × 合格率 | 世界级目标 >85%", { x:0.8, y:4.2, w:9, h:0.4, fontSize:13, fontFace:"Arial", color:C.S });

// Slide 2: OEE计算详解
let s = pptx.addSlide(); setBg(s); addTopBar(s, C.TE); addTitleBand(s, "OEE 计算详解", "Overall Equipment Effectiveness");
s.addShape(S.roundRect, { x:2, y:1.2, w:9.33, h:0.7, fill:{color:C.P}, transparency:8, rectRadius:0.1 });
s.addText("OEE = 可用率 × 性能率 × 合格率", { x:2, y:1.25, w:9.33, h:0.6, fontFace:"Arial Black", fontSize:24, color:C.P, align:"center", valign:"middle" });
const factors = [
  { n:"可用率 Availability", f:"(计划时间 − 停机时间) / 计划时间", t:">90%", e:"例：计划440min，停机30min\n可用率 = (440−30)/440 = 93.2%", c:C.TE },
  { n:"性能率 Performance", f:"(理想节拍 × 产出数量) / 运行时间", t:">95%", e:"例：理想节拍1.0s，产出35000件\n性能率 = 35000/24600 = 87.5%", c:C.W },
  { n:"合格率 Quality", f:"合格品数量 / 总产出数量", t:">99.9%", e:"例：产出35000，不良350，废品100\n合格率 = 34550/35000 = 98.7%", c:C.G }
];
factors.forEach((f,i) => {
  let x = 0.4 + i*4.3;
  s.addShape(S.roundRect, { x, y:2.1, w:4, h:2.8, fill:{color:C.A}, shadow:{type:"outer",color:"000000",blur:6,offset:2,angle:135,opacity:0.1}, rectRadius:0.08 });
  s.addShape(S.rect, { x, y:2.1, w:4, h:0.3, fill:{color:f.c}, line:{color:f.c,width:0} });
  s.addText(f.n, { x:x+0.15, y:2.12, w:3.7, h:0.28, fontFace:"Arial Black", fontSize:11, color:C.A, align:"center", bold:true, margin:0 });
  s.addText(f.f, { x:x+0.15, y:2.48, w:3.7, h:0.4, fontFace:"Arial", fontSize:10, color:C.T, align:"center" });
  s.addText("目标: "+f.t, { x:x+0.15, y:2.9, w:3.7, h:0.25, fontFace:"Arial Black", fontSize:10, color:f.c, align:"center", bold:true });
  s.addText(f.e, { x:x+0.15, y:3.2, w:3.7, h:1.5, fontFace:"Arial", fontSize:9, color:C.TL, valign:"top" });
});
s.addShape(S.roundRect, { x:2, y:5.2, w:9.33, h:0.5, fill:{color:C.P}, rectRadius:0.06 });
s.addText("综合 OEE = 93.2% × 87.5% × 98.7% = 80.3%", { x:2, y:5.2, w:9.33, h:0.5, fontFace:"Arial Black", fontSize:18, color:C.A, align:"center", valign:"middle" });
addFooter(s, "OEE 衡量设备的有效利用程度 | 识别六大损失是提升OEE的关键");

// Slide 3: 六大损失
s = pptx.addSlide(); setBg(s); addTopBar(s, C.TE); addTitleBand(s, "OEE 六大损失分析", "Six Big Losses");
const losses = [
  { n:"设备故障", dim:"可用率", t:"45min", p:"32%", col:C.D },
  { n:"换型调整", dim:"可用率", t:"35min", p:"25%", col:C.W },
  { n:"空转短停", dim:"性能率", t:"18min", p:"13%", col:C.W },
  { n:"速度降低", dim:"性能率", t:"20min", p:"14%", col:C.TE },
  { n:"过程缺陷", dim:"合格率", t:"12min", p:"9%", col:C.D },
  { n:"开机废品", dim:"合格率", t:"5min", p:"4%", col:C.TE }
];
losses.forEach((l,i) => {
  let col=i%3, row=Math.floor(i/3), x=0.4+col*4.3, y=1.2+row*2.2;
  s.addShape(S.roundRect, { x, y, w:4, h:2.0, fill:{color:C.A}, shadow:{type:"outer",color:"000000",blur:4,offset:1,angle:135,opacity:0.08}, rectRadius:0.08 });
  s.addShape(S.rect, { x, y, w:4, h:0.26, fill:{color:l.col}, line:{color:l.col,width:0} });
  s.addText(l.n, { x:x+0.15, y:y+0.02, w:3.7, h:0.24, fontFace:"Arial Black", fontSize:12, color:C.A, bold:true, align:"center", margin:0 });
  s.addText("影响维度: "+l.dim+"  |  时间损失: "+l.t, { x:x+0.15, y:y+0.32, w:3.7, h:0.25, fontFace:"Arial", fontSize:10, color:C.TL, align:"center" });
  s.addText(l.p, { x:x+0.15, y:y+0.65, w:1.5, h:0.6, fontFace:"Arial Black", fontSize:32, color:l.col, bold:true });
  s.addText("占比", { x:x+1.65, y:y+0.75, w:0.8, h:0.3, fontFace:"Arial", fontSize:10, color:C.TL });
  s.addShape(S.rect, { x:x+0.15, y:y+1.35, w:3.7, h:0.12, fill:{color:"E2E8F0"}, rectRadius:0.04 });
  let fillW = (parseInt(l.p)/35) * 3.7;
  s.addShape(S.rect, { x:x+0.15, y:y+1.35, w:fillW, h:0.12, fill:{color:l.col}, rectRadius:0.04 });
  s.addText("紧固件行业重点：减少故障和换型损失可显著提升OEE", { x:x+0.15, y:y+1.6, w:3.7, h:0.3, fontFace:"Arial", fontSize:8.5, color:C.TL });
});
addFooter(s, "六大损失是OEE下降的根本原因 | 针对性改善可快速提升设备效率");

// Slide 4: TPM八大支柱
s = pptx.addSlide(); setBg(s); addTopBar(s, C.TE); addTitleBand(s, "TPM 八大支柱", "8 Pillars of TPM");
const pillars = [
  { n:"自主维护", d:"操作员日常保养清扫点检", c:C.TE, num:"01" },
  { n:"计划维护", d:"预防性/预测性维护体系", c:C.P, num:"02" },
  { n:"个别改善", d:"设备损失专项改善攻关", c:C.W, num:"03" },
  { n:"教育训练", d:"维护技能体系化培训", c:C.G, num:"04" },
  { n:"初期管理", d:"新设备快速稳定投产", c:C.TE, num:"05" },
  { n:"品质维护", d:"设备精度保障与提升", c:C.D, num:"06" },
  { n:"事务改善", d:"办公流程精益化", c:C.P, num:"07" },
  { n:"安全环境", d:"零灾害零公害目标", c:C.G, num:"08" }
];
pillars.forEach((pl,i) => {
  let col=i%4, row=Math.floor(i/4), x=0.4+col*3.2, y=1.2+row*2.4;
  s.addShape(S.roundRect, { x, y, w:3, h:2.2, fill:{color:C.A}, shadow:{type:"outer",color:"000000",blur:4,offset:1,angle:135,opacity:0.08}, rectRadius:0.08 });
  s.addShape(S.rect, { x, y, w:3, h:0.28, fill:{color:pl.c}, line:{color:pl.c,width:0} });
  s.addText(pl.num, { x:x+0.1, y:y+0.02, w:0.5, h:0.26, fontFace:"Arial Black", fontSize:10, color:C.A, margin:0 });
  s.addText(pl.n, { x:x+0.6, y:y+0.02, w:2.2, h:0.26, fontFace:"Arial Black", fontSize:11, color:C.A, align:"center", bold:true, margin:0 });
  s.addText(pl.d, { x:x+0.15, y:y+0.36, w:2.7, h:0.3, fontFace:"Arial", fontSize:9, color:C.TL, align:"center" });
  s.addShape(S.ellipse, { x:x+1.0, y:y+0.8, w:1, h:1, fill:{color:pl.c}, transparency:15, line:{color:pl.c,width:0} });
  s.addText(pl.n.charAt(0), { x:x+1.0, y:y+0.8, w:1, h:1, fontFace:"Arial Black", fontSize:28, color:pl.c, align:"center", valign:"middle" });
});
addFooter(s, "八大支柱协同运作 | 全员参与是TPM的核心理念");

// Slide 5: 自主维护七步法
s = pptx.addSlide(); setBg(s); addTopBar(s, C.TE); addTitleBand(s, "自主维护七步法", "7 Steps of Autonomous Maintenance");
const steps = ["1\n初期清扫","2\n发生源对策","3\n临时基准","4\n总点检","5\n自主点检","6\n标准化","7\n持续改善"];
steps.forEach((st,i) => {
  let x = 0.5 + i*1.8;
  s.addShape(S.roundRect, { x, y:1.35, w:1.6, h:0.55, fill:{color:C.TE}, rectRadius:0.08 });
  s.addText(st, { x, y:1.37, w:1.6, h:0.5, fontFace:"Arial Black", fontSize:10, color:C.A, bold:true, align:"center", valign:"middle" });
  if(i<6) {
    s.addShape(S.rect, { x:x+1.6, y:1.55, w:0.2, h:0.04, fill:{color:C.TE}, line:{color:C.TE,width:0} });
    s.addShape(S.rtTriangle, { x:x+1.75, y:1.48, w:0.15, h:0.18, fill:{color:C.TE}, line:{color:C.TE,width:0} });
  }
});
s.addShape(S.roundRect, { x:0.5, y:2.4, w:12.33, h:2.8, fill:{color:C.P}, transparency:5, rectRadius:0.1 });
s.addText("微缺陷放大效应 — 1个重大事故背后可能有1000个微缺陷！", { x:0.8, y:2.5, w:11.7, h:0.4, fontFace:"Arial Black", fontSize:16, color:C.P, bold:true });
const chain = ["1个微缺陷","→ 10个","→ 1个中缺陷","→ 10个","→ 1个大缺陷","→ 10个","→ 1次故障","→ 10个","→ 1次重大事故"];
chain.forEach((c,i) => {
  let x = 0.8 + i*1.35;
  let bg = i===8 ? C.D : C.TE;
  s.addShape(S.roundRect, { x, y:3.0, w:1.2, h:0.45, fill:{color:bg}, rectRadius:0.06 });
  s.addText(c, { x, y:3.02, w:1.2, h:0.42, fontFace:"Arial Black", fontSize:8, color:C.A, align:"center", valign:"middle", bold:true });
});
s.addText("清扫即点检：通过日常清扫发现设备微缺陷，在故障发生前消除隐患", { x:0.8, y:3.7, w:11.7, h:0.35, fontFace:"Arial", fontSize:12, color:C.TL });
addFooter(s, "自主维护是TPM的基石 | 操作员是设备的第一责任人");

// Slide 6: OEE行业基准与紧固件KPI
s = pptx.addSlide(); setBg(s); addTopBar(s, C.TE); addTitleBand(s, "OEE 行业基准与紧固件KPI", "OEE Benchmarks & Fastener KPIs");
statCard(s, 0.4, 1.3, ">90%", "世界级\nWorld Class", C.G, "所有三项指标>90%");
statCard(s, 3.6, 1.3, "80-90%", "优秀\nExcellent", C.TE, "行业领先水平");
statCard(s, 6.8, 1.3, "65-80%", "发展中\nDeveloping", C.W, "有较大改善空间");
statCard(s, 10.0, 1.3, "<65%", "落后\nPoor", C.D, "急需系统性改善");
s.addShape(S.rect, { x:0.5, y:3.2, w:12.33, h:0.04, fill:{color:C.P}, line:{color:C.P,width:0} });
s.addText("紧固件制造关键KPI", { x:0.8, y:3.4, w:5, h:0.4, fontFace:"Arial Black", fontSize:18, color:C.P, bold:true });
const kpiRows = [
  ["KPI", "当前水平", "改善目标", "世界级标准"],
  ["OEE", "72%", "85%", ">90%"],
  ["换型时间", "60min", "<10min", "<5min"],
  ["不良率", "2.5%", "1.0%", "<0.1%"],
  ["库存周转", "<14天", "<7天", "<3天"],
  ["交付准时率", "90%", "98%", ">99%"]
];
const kpiW = [3.0, 3.0, 3.0, 3.33];
kpiRows.forEach((row,ri) => {
  row.forEach((cell,ci) => {
    let x = 0.4 + ci*kpiW[ci], y = 3.9 + ri*0.42;
    let bg = ri===0 ? C.P : (ri%2===1 ? C.A : C.L);
    let txtColor = ri===0 ? C.A : C.T;
    s.addShape(S.rect, { x, y, w:kpiW[ci]-0.05, h:0.38, fill:{color:bg} });
    s.addText(cell, { x:x+0.1, y:y+0.04, w:kpiW[ci]-0.2, h:0.3, fontFace:ri===0?"Arial Black":"Arial", fontSize:10, color:txtColor, align:"center", valign:"middle", margin:0 });
  });
});
addFooter(s, "OEE从72%提升至85%是紧固件企业3年精益转型的核心目标");

pptx.writeFile({ fileName: path.join(OUT, "02-TPM与OEE详解.pptx") }).then(() => {
  console.log("✅ 02-TPM与OEE详解.pptx created!");
}).catch(err => console.error("Error:", err));
