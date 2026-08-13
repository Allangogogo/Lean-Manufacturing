// 03 - 价值流图 VSM 详解
const PptxGenJS = require("pptxgenjs");
const path = require("path");
const OUT = __dirname;

const C = { P:"1E2761", S:"CADCFC", A:"FFFFFF", L:"F8FAFC", T:"1E293B", TL:"64748B", G:"059669", W:"D97706", D:"DC2626", TE:"0D9488", TL2:"5EEAD4" };
const W = 13.33, H = 7.5;

let pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE"; pptx.title = "价值流图VSM详解"; pptx.author = "精益工具知识库";
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
  slide.addShape(S.roundRect, { x:x, y:y, w:2.8, h:1.5, fill:{color:C.A}, transparency:10, line:{color:color, width:1}, rectRadius:0.08 });
  slide.addShape(S.rect, { x:x, y:y, w:2.8, h:0.06, fill:{color:color}, line:{color:color,width:0} });
  slide.addText(num, { x:x, y:y+0.15, w:2.8, h:0.6, fontFace:"Arial Black", fontSize:28, color:C.A, align:"center", bold:true, valign:"middle" });
  slide.addText(label, { x:x, y:y+0.75, w:2.8, h:0.35, fontFace:"Arial", fontSize:11, color:C.S, align:"center", valign:"middle" });
  if(sub) slide.addText(sub, { x:x, y:y+1.05, w:2.8, h:0.35, fontFace:"Arial", fontSize:9, color:C.TL, align:"center", valign:"middle" });
}

// ======== Slide 1: Dark Chapter Cover ========
let s1 = pptx.addSlide();
s1.addShape(S.rect, { x:0, y:0, w:W, h:H, fill:{color:C.P}, line:{color:C.P,width:0} });
addTopBar(s1, C.TE, 0.12);
s1.addShape(S.rect, { x:10.5, y:0, w:2.83, h:H, fill:{color:"0F172A"}, transparency:70, line:{color:"0F172A",width:0} });
s1.addShape(S.ellipse, { x:11.0, y:1.0, w:2.0, h:2.0, fill:{color:C.TE}, transparency:80, line:{color:C.TE,width:0} });
s1.addShape(S.ellipse, { x:11.5, y:3.0, w:1.5, h:1.5, fill:{color:C.A}, transparency:85, line:{color:C.A,width:0} });
s1.addText("03", { x:0.8, y:0.8, w:3, h:1.2, fontSize:80, fontFace:"Arial Black", color:C.TL2, bold:true });
s1.addText("价值流图 VSM", { x:0.8, y:2.2, w:9, h:0.9, fontSize:40, fontFace:"Arial Black", color:C.A, bold:true });
s1.addText("Value Stream Mapping", { x:0.8, y:3.2, w:9, h:0.5, fontSize:18, fontFace:"Arial", color:C.S });
s1.addShape(S.rect, { x:0.8, y:3.9, w:3, h:0.05, fill:{color:C.TE}, line:{color:C.TE,width:0} });
s1.addText("从原材料到成品的全流程价值流可视化分析 | 识别浪费、设计未来状态", { x:0.8, y:4.2, w:9, h:0.4, fontSize:13, fontFace:"Arial", color:C.S });

// ======== Slide 2: VSM定义与目的 ========
let s2 = pptx.addSlide(); setBg(s2); addTopBar(s2, C.TE); addTitleBand(s2, "VSM 定义与目的", "What is Value Stream Mapping?");
s2.addShape(S.roundRect, { x:0.5, y:1.2, w:5.5, h:1.2, fill:{color:C.P}, transparency:5, rectRadius:0.1 });
s2.addText("价值流图（VSM）是一种精益制造工具，用于可视化描绘从原材料到成品交付给客户的整个生产流程中的物料流和信息流，目的是识别系统中的浪费（Muda）并找到改善机会。", { x:0.7, y:1.3, w:5.1, h:1.0, fontFace:"Arial", fontSize:11, color:C.T, valign:"top" });
s2.addText("VSM 核心目的", { x:6.5, y:1.2, w:6.3, h:0.4, fontFace:"Arial Black", fontSize:16, color:C.P, bold:true });
const purposes = [
  { icon:"①", t:"全面识别浪费", c:C.D },
  { icon:"②", t:"量化流程数据", c:C.TE },
  { icon:"③", t:"可视化全流程", c:C.P },
  { icon:"④", t:"设计未来状态", c:C.G },
  { icon:"⑤", t:"跨部门协同", c:C.W },
  { icon:"⑥", t:"持续改善基线", c:C.TE }
];
purposes.forEach(function(p,i) {
  var col=i%3, row=Math.floor(i/3), x=6.5+col*2.2, y=1.7+row*1.1;
  s2.addShape(S.roundRect, { x:x, y:y, w:2.0, h:0.95, fill:{color:C.A}, shadow:{type:"outer",color:"000000",blur:4,offset:1,angle:135,opacity:0.08}, rectRadius:0.08 });
  s2.addShape(S.rect, { x:x, y:y, w:2.0, h:0.24, fill:{color:p.c}, line:{color:p.c,width:0} });
  s2.addText(p.icon, { x:x+0.05, y:y+0.28, w:0.4, h:0.35, fontFace:"Arial Black", fontSize:14, align:"center" });
  s2.addText(p.t, { x:x+0.5, y:y+0.3, w:1.4, h:0.3, fontFace:"Arial Black", fontSize:10, color:C.T, bold:true, valign:"middle" });
  s2.addText("精益核心原则", { x:x+0.05, y:y+0.62, w:1.9, h:0.25, fontFace:"Arial", fontSize:8, color:C.TL, align:"center" });
});
s2.addShape(S.rect, { x:0.5, y:4.2, w:12.33, h:0.04, fill:{color:C.P}, line:{color:C.P,width:0} });
s2.addText("精益五大原则", { x:0.8, y:4.35, w:3, h:0.4, fontFace:"Arial Black", fontSize:14, color:C.P, bold:true });
var principles = ["1. 价值 Value", "2. 价值流 Value Stream", "3. 流动 Flow", "4. 拉动 Pull", "5. 尽善尽美 Perfection"];
principles.forEach(function(pr,i) {
  var x = 0.5 + i*2.5;
  s2.addShape(S.roundRect, { x:x, y:4.85, w:2.35, h:0.55, fill:{color:C.TE}, transparency:10, line:{color:C.TE,width:0.5}, rectRadius:0.06 });
  s2.addText(pr, { x:x+0.1, y:4.87, w:2.15, h:0.5, fontFace:"Arial", fontSize:9, color:C.T, valign:"middle" });
});
addFooter(s2, "VSM是精益转型的起点 | 先看清现状，再设计未来");

// ======== Slide 3: VSM实施步骤 ========
var s3 = pptx.addSlide(); setBg(s3); addTopBar(s3, C.TE); addTitleBand(s3, "VSM 实施步骤", "7 Steps to Value Stream Mapping");
var vsmSteps = [
  { t:"选择\n产品族", d:"按价值流选择\n关键产品族", c:C.P },
  { t:"绘制\n当前状态", d:"现场收集数据\n绘制现状流程图", c:C.TE },
  { t:"分析\n浪费", d:"识别7大浪费\n量化损失", c:C.D },
  { t:"设计\n未来状态", d:"理想流程设计\n目标指标设定", c:C.G },
  { t:"制定\n改善计划", d:"分解改善项目\n制定实施路线", c:C.W },
  { t:"实施\n改善", d:"执行改善计划\n跟踪进度", c:C.TE },
  { t:"标准化\n持续改善", d:"固化改善成果\n建立机制", c:C.P }
];
vsmSteps.forEach(function(st,i) {
  var x = 0.3 + i*1.85;
  s3.addShape(S.roundRect, { x:x, y:1.3, w:1.7, h:1.0, fill:{color:st.c}, rectRadius:0.1 });
  s3.addText(String(i+1), { x:x, y:1.35, w:1.7, h:0.4, fontFace:"Arial Black", fontSize:22, color:C.A, bold:true, align:"center", valign:"middle" });
  s3.addText(st.t, { x:x, y:1.72, w:1.7, h:0.55, fontFace:"Arial Black", fontSize:9, color:C.A, bold:true, align:"center", valign:"middle" });
  if(i < 6) {
    s3.addShape(S.rect, { x:x+1.7, y:1.65, w:0.15, h:0.04, fill:{color:C.TE}, line:{color:C.TE,width:0} });
    s3.addShape(S.rightArrow, { x:x+1.8, y:1.55, w:0.18, h:0.24, fill:{color:C.TE}, line:{color:C.TE,width:0} });
  }
  s3.addText(st.d, { x:x-0.05, y:2.45, w:1.8, h:0.5, fontFace:"Arial", fontSize:8, color:C.TL, align:"center" });
});
s3.addShape(S.roundRect, { x:0.5, y:3.2, w:12.33, h:2.2, fill:{color:C.P}, transparency:5, rectRadius:0.1 });
s3.addText("当前状态图 vs 未来状态图", { x:0.8, y:3.3, w:11.7, h:0.4, fontFace:"Arial Black", fontSize:16, color:C.P, bold:true });
var compare = [
  { label:"当前状态图 Current State", desc:"如实反映现有流程，暴露问题和浪费", items:["现场实测数据","实际库存水平","真实节拍时间","现有信息流"], c:C.D },
  { label:"未来状态图 Future State", desc:"设计理想流程，设定改善目标和方向", items:["目标节拍时间","目标库存水平","拉动式生产","连续流设计"], c:C.G }
];
compare.forEach(function(comp,ci) {
  var x = 0.8 + ci*6.0;
  s3.addShape(S.roundRect, { x:x, y:3.8, w:5.6, h:1.4, fill:{color:C.A}, shadow:{type:"outer",color:"000000",blur:4,offset:1,angle:135,opacity:0.08}, rectRadius:0.08 });
  s3.addShape(S.rect, { x:x, y:3.8, w:5.6, h:0.3, fill:{color:comp.c}, line:{color:comp.c,width:0} });
  s3.addText(comp.label, { x:x+0.15, y:3.82, w:5.3, h:0.28, fontFace:"Arial Black", fontSize:11, color:C.A, bold:true, align:"center", margin:0 });
  s3.addText(comp.desc, { x:x+0.15, y:4.15, w:5.3, h:0.25, fontFace:"Arial", fontSize:9, color:C.TL, align:"center" });
  comp.items.forEach(function(item,ii) {
    s3.addText("• " + item, { x:x+0.2, y:4.45+ii*0.22, w:5.2, h:0.2, fontFace:"Arial", fontSize:9, color:C.T });
  });
});
addFooter(s3, "VSM不是一次性项目，而是持续改善的循环 | 建议每年至少更新一次");

// ======== Slide 4: VSM当前状态图 ========
var s4 = pptx.addSlide(); setBg(s4); addTopBar(s4, C.TE); addTitleBand(s4, "VSM 当前状态图", "Current State Map");
s4.addText("当前状态图绘制要素 — 以紧固件生产为例", { x:0.5, y:1.15, w:12.33, h:0.4, fontFace:"Arial Black", fontSize:16, color:C.P, bold:true });
var processes = [
  { n:"冷镦\nCold Forging", t:"2.5min", u:"85%", d:"2000" },
  { n:"搓丝\nThread Roll", t:"1.8min", u:"90%", d:"2500" },
  { n:"热处理\nHeat Treat.", t:"45min", u:"75%", d:"500" },
  { n:"表面处理\nSurface Tr.", t:"30min", u:"80%", d:"800" },
  { n:"分选\nInspection", t:"0.5min", u:"95%", d:"3000" },
  { n:"包装\nPackaging", t:"0.3min", u:"98%", d:"5000" }
];
processes.forEach(function(p,i) {
  var x = 0.4 + i*2.1;
  s4.addShape(S.rect, { x:x, y:1.7, w:1.9, h:1.5, fill:{color:C.A}, line:{color:C.P,width:1} });
  s4.addText(p.n, { x:x, y:1.75, w:1.9, h:0.4, fontFace:"Arial Black", fontSize:10, color:C.P, bold:true, align:"center" });
  s4.addShape(S.rect, { x:x, y:2.15, w:1.9, h:0.04, fill:{color:C.P}, line:{color:C.P,width:0} });
  s4.addText("CT=" + p.t, { x:x, y:2.25, w:1.9, h:0.25, fontFace:"Arial", fontSize:9, color:C.T, align:"center" });
  s4.addText("UP=" + p.u, { x:x, y:2.5, w:1.9, h:0.25, fontFace:"Arial", fontSize:9, color:C.T, align:"center" });
  s4.addText("Batch=" + p.d, { x:x, y:2.75, w:1.9, h:0.25, fontFace:"Arial", fontSize:8, color:C.TL, align:"center" });
  if(i < 5) {
    s4.addShape(S.diamond, { x:x+1.95, y:1.82, w:0.2, h:0.3, fill:{color:C.W}, line:{color:C.W,width:0} });
    s4.addText(String(500+i*200), { x:x+1.93, y:2.16, w:0.26, h:0.3, fontFace:"Arial", fontSize:7, color:C.TL, align:"center" });
    s4.addShape(S.rightArrow, { x:x+2.15, y:2.65, w:0.12, h:0.2, fill:{color:C.D}, line:{color:C.D,width:0} });
    s4.addText("推", { x:x+2.12, y:2.85, w:0.2, h:0.2, fontFace:"Arial", fontSize:7, color:C.D, align:"center" });
  }
});
s4.addShape(S.rect, { x:0.4, y:3.5, w:12.5, h:0.06, fill:{color:C.P}, line:{color:C.P,width:0} });
s4.addText("Lead Time = CT之和(49.9min) + 等待时间(~72h) = ~75h", { x:0.5, y:3.65, w:12, h:0.3, fontFace:"Arial Black", fontSize:12, color:C.P, bold:true });
var timeline = [
  { l:"加工时间\nProcessing", v:"49.9\nmin", c:C.G },
  { l:"等待时间\nWaiting", v:"~72\nhour", c:C.D },
  { l:"交付周期\nLead Time", v:"~75\nhour", c:C.P },
  { l:"增值比\nVA Ratio", v:"1.1\n%", c:C.W }
];
timeline.forEach(function(tl,i) {
  var x = 0.4 + i*3.1;
  s4.addShape(S.roundRect, { x:x, y:4.1, w:2.9, h:1.2, fill:{color:C.A}, shadow:{type:"outer",color:"000000",blur:4,offset:1,angle:135,opacity:0.08}, rectRadius:0.08 });
  s4.addShape(S.rect, { x:x, y:4.1, w:2.9, h:0.26, fill:{color:tl.c}, line:{color:tl.c,width:0} });
  s4.addText(tl.l, { x:x, y:4.12, w:2.9, h:0.24, fontFace:"Arial Black", fontSize:9, color:C.A, bold:true, align:"center", margin:0 });
  s4.addText(tl.v, { x:x, y:4.45, w:2.9, h:0.5, fontFace:"Arial Black", fontSize:20, color:tl.c, bold:true, align:"center" });
});
addFooter(s4, "当前状态图揭示真实浪费 | 增值比通常仅1-5%，改善空间巨大");

// ======== Slide 5: VSM未来状态图 ========
var s5 = pptx.addSlide(); setBg(s5); addTopBar(s5, C.TE); addTitleBand(s5, "VSM 未来状态图", "Future State Map — Design Principles");
s5.addText("未来状态设计四大原则", { x:0.5, y:1.15, w:12.33, h:0.4, fontFace:"Arial Black", fontSize:16, color:C.P, bold:true });
var futureP = [
  { t:"按节拍生产 Takt Time", d:"根据客户需求速率设定生产节拍\n消除过量生产浪费", c:C.G },
  { t:"连续流 Continuous Flow", d:"消除工序间等待\n实现一件流或小批量流", c:C.TE },
  { t:"拉动式生产 Pull System", d:"后工序向前工序取货\n用看板控制生产", c:C.P },
  { t:"均衡化生产 Heijunka", d:"平准化产品组合\n减少波动和浪费", c:C.W }
];
futureP.forEach(function(fp,i) {
  var col=i%2, row=Math.floor(i/2), x=0.5+col*6.3, y=1.65+row*1.6;
  s5.addShape(S.roundRect, { x:x, y:y, w:6.0, h:1.45, fill:{color:C.A}, shadow:{type:"outer",color:"000000",blur:4,offset:1,angle:135,opacity:0.08}, rectRadius:0.08 });
  s5.addShape(S.rect, { x:x, y:y, w:6.0, h:0.3, fill:{color:fp.c}, line:{color:fp.c,width:0} });
  s5.addText(fp.t, { x:x+0.15, y:y+0.02, w:5.7, h:0.28, fontFace:"Arial Black", fontSize:11, color:C.A, bold:true, align:"center", margin:0 });
  s5.addText(fp.d, { x:x+0.15, y:y+0.38, w:5.7, h:0.35, fontFace:"Arial", fontSize:10, color:C.T, align:"center" });
  s5.addShape(S.rect, { x:x+0.8, y:y+0.85, w:1.2, h:0.35, fill:{color:fp.c}, transparency:20, rectRadius:0.04 });
  s5.addText("工序A", { x:x+0.8, y:y+0.87, w:1.2, h:0.3, fontFace:"Arial", fontSize:8, color:C.T, align:"center", valign:"middle" });
  s5.addShape(S.rightArrow, { x:x+2.0, y:y+0.9, w:0.3, h:0.25, fill:{color:fp.c}, line:{color:fp.c,width:0} });
  s5.addShape(S.rect, { x:x+2.3, y:y+0.85, w:1.2, h:0.35, fill:{color:fp.c}, transparency:20, rectRadius:0.04 });
  s5.addText("工序B", { x:x+2.3, y:y+0.87, w:1.2, h:0.3, fontFace:"Arial", fontSize:8, color:C.T, align:"center", valign:"middle" });
});
// Target metrics
s5.addShape(S.roundRect, { x:0.5, y:5.1, w:12.33, h:0.45, fill:{color:C.G}, transparency:10, line:{color:C.G,width:0.5}, rectRadius:0.06 });
s5.addText("目标指标：Lead Time -50% | 库存 -60% | 增值比 >5% | OEE >85%", { x:0.5, y:5.12, w:12.33, h:0.42, fontFace:"Arial Black", fontSize:13, color:C.G, align:"center", valign:"middle" });
addFooter(s5, "未来状态图是改善的蓝图 | 从现状到未来需要分阶段实施");

// ======== Slide 6: 紧固件行业VSM应用 ========
var s6 = pptx.addSlide(); setBg(s6); addTopBar(s6, C.TE); addTitleBand(s6, "紧固件行业 VSM 应用", "VSM in Fastener Manufacturing");
s6.addText("典型紧固件生产价值流", { x:0.5, y:1.15, w:12.33, h:0.4, fontFace:"Arial Black", fontSize:16, color:C.P, bold:true });
var fastenerSteps = [
  { n:"冷镦", sub:"Cold Forging", ct:"2.5", up:"85%", bt:"500", c:C.P },
  { n:"搓丝", sub:"Thread Roll", ct:"1.8", up:"90%", bt:"700", c:C.TE },
  { n:"热处理", sub:"Heat Treat.", ct:"45", up:"75%", bt:"1200", c:C.W },
  { n:"表面处理", sub:"Surface Tr.", ct:"30", up:"80%", bt:"1000", c:C.D },
  { n:"分选", sub:"Inspection", ct:"0.5", up:"95%", bt:"300", c:C.G },
  { n:"包装", sub:"Packaging", ct:"0.3", up:"98%", bt:"200", c:C.TE }
];
fastenerSteps.forEach(function(fs,i) {
  var x = 0.3 + i*2.1;
  s6.addShape(S.roundRect, { x:x, y:1.7, w:1.95, h:1.8, fill:{color:C.A}, shadow:{type:"outer",color:"000000",blur:4,offset:1,angle:135,opacity:0.08}, rectRadius:0.08 });
  s6.addShape(S.rect, { x:x, y:1.7, w:1.95, h:0.28, fill:{color:fs.c}, line:{color:fs.c,width:0} });
  s6.addText(fs.n, { x:x, y:1.72, w:1.95, h:0.26, fontFace:"Arial Black", fontSize:11, color:C.A, bold:true, align:"center", margin:0 });
  s6.addText(fs.sub, { x:x+0.1, y:2.0, w:1.75, h:0.2, fontFace:"Arial", fontSize:7, color:C.TL, align:"center" });
  s6.addText("CT: " + fs.ct + " min", { x:x+0.1, y:2.25, w:1.75, h:0.25, fontFace:"Arial", fontSize:9, color:C.T });
  s6.addText("Uptime: " + fs.up, { x:x+0.1, y:2.5, w:1.75, h:0.25, fontFace:"Arial", fontSize:9, color:C.T });
  s6.addText("Inventory: " + fs.bt, { x:x+0.1, y:2.75, w:1.75, h:0.25, fontFace:"Arial", fontSize:9, color:C.W });
  s6.addShape(S.rect, { x:x+0.2, y:3.1, w:1.55, h:0.08, fill:{color:"E2E8F0"}, rectRadius:0.03 });
  var fillPct = Math.min(parseFloat(fs.up) / 100, 1);
  s6.addShape(S.rect, { x:x+0.2, y:3.1, w:1.55*fillPct, h:0.08, fill:{color:fs.c}, rectRadius:0.03 });
  s6.addText(fs.up, { x:x+0.2, y:3.22, w:1.55, h:0.2, fontFace:"Arial", fontSize:8, color:C.TL, align:"center" });
});
// Summary boxes
s6.addShape(S.roundRect, { x:0.5, y:3.8, w:12.33, h:1.6, fill:{color:C.P}, transparency:5, rectRadius:0.1 });
s6.addText("关键改善机会", { x:0.8, y:3.9, w:11.7, h:0.35, fontFace:"Arial Black", fontSize:14, color:C.P, bold:true });
var opportunities = [
  { t:"热处理瓶颈", d:"CT=45min是最大瓶颈，建议增加设备或优化装炉量", c:C.D, num:"01" },
  { t:"换型时间长", d:"冷镦换型>60min，实施SMED可降至<10min", c:C.W, num:"02" },
  { t:"在制品积压", d:"总WIP达3900件，拉动式可减少60%", c:C.TE, num:"03" },
  { t:"信息流断裂", d:"计划到现场信息传递滞后，建议电子看板", c:C.G, num:"04" }
];
opportunities.forEach(function(opp,i) {
  var x = 0.8 + i*3.0;
  s6.addShape(S.roundRect, { x:x, y:4.3, w:2.8, h:1.0, fill:{color:C.A}, rectRadius:0.08 });
  s6.addShape(S.rect, { x:x, y:4.3, w:2.8, h:0.22, fill:{color:opp.c}, line:{color:opp.c,width:0} });
  s6.addText(opp.num + " " + opp.t, { x:x+0.1, y:4.32, w:2.6, h:0.2, fontFace:"Arial Black", fontSize:9, color:C.A, bold:true, margin:0 });
  s6.addText(opp.d, { x:x+0.1, y:4.58, w:2.6, h:0.65, fontFace:"Arial", fontSize:8, color:C.T, valign:"top" });
});
addFooter(s6, "紧固件行业VSM核心：减少热处理瓶颈和换型时间 | 建立拉动式生产体系");

// ======== Slide 7: VSM关键指标 ========
var s7 = pptx.addSlide(); setBg(s7); addTopBar(s7, C.TE); addTitleBand(s7, "VSM 关键指标与KPI", "Key Performance Indicators");
s7.addText("VSM核心KPI追踪表", { x:0.5, y:1.15, w:12.33, h:0.4, fontFace:"Arial Black", fontSize:16, color:C.P, bold:true });
var kpiData = [
  ["KPI指标", "当前状态", "改善目标", "6个月后", "12个月后", "状态"],
  ["交付周期 Lead Time", "75h", "38h", "55h", "35h", "改善中"],
  ["在制品库存 WIP", "3900件", "1560件", "2500件", "1400件", "改善中"],
  ["设备综合效率 OEE", "72%", "85%", "78%", "87%", "进行中"],
  ["增值比 VA Ratio", "1.1%", "5%", "3.2%", "6%", "改善中"],
  ["换型时间 Changeover", "60min", "<10min", "25min", "<8min", "快速改善"],
  ["不良率 Defect Rate", "2.5%", "0.5%", "1.2%", "0.4%", "改善中"],
  ["交付准时率 OTD", "88%", "98%", "93%", "99%", "接近目标"],
  ["库存周转天数", "14天", "5天", "9天", "4天", "改善中"]
];
var colW = [2.2, 2.0, 2.0, 2.0, 2.0, 1.8];
kpiData.forEach(function(row,ri) {
  row.forEach(function(cell,ci) {
    var x = 0.4;
    for(var k=0;k<ci;k++) x += colW[k];
    var y = 1.7 + ri*0.42;
    var bg = ri===0 ? C.P : (ri%2===1 ? C.A : C.L);
    var txtColor = ri===0 ? C.A : C.T;
    var isStatusCol = ci===5;
    if(isStatusCol && ri>0) {
      bg = cell === "接近目标" ? C.G : C.W;
      txtColor = C.A;
    }
    s7.addShape(S.rect, { x:x, y:y, w:colW[ci]-0.05, h:0.38, fill:{color:bg} });
    s7.addText(cell, { x:x+0.08, y:y+0.04, w:colW[ci]-0.16, h:0.3, fontFace:ri===0?"Arial Black":"Arial", fontSize:9, color:txtColor, align:ci===0?"left":"center", valign:"middle", margin:0 });
  });
});
// Legend
s7.addShape(S.rect, { x:0.4, y:5.6, w:0.4, h:0.2, fill:{color:C.G} });
s7.addText("已达到/接近目标", { x:0.9, y:5.6, w:2.5, h:0.2, fontFace:"Arial", fontSize:9, color:C.T, valign:"middle" });
s7.addShape(S.rect, { x:3.6, y:5.6, w:0.4, h:0.2, fill:{color:C.W} });
s7.addText("改善中", { x:4.1, y:5.6, w:1.5, h:0.2, fontFace:"Arial", fontSize:9, color:C.T, valign:"middle" });
s7.addShape(S.roundRect, { x:0.5, y:6.0, w:12.33, h:0.4, fill:{color:C.P}, transparency:5, rectRadius:0.06 });
s7.addText("改善路径：先缩短换型时间(QUICK WIN) → 建立拉动系统 → 优化瓶颈工序 → 持续改善", { x:0.7, y:6.02, w:11.9, h:0.36, fontFace:"Arial Black", fontSize:11, color:C.P, align:"center", valign:"middle" });
addFooter(s7, "KPI追踪是VSM持续改善的保障 | 建议每月回顾一次关键指标");

// ======== Write file ========
pptx.writeFile({ fileName: path.join(OUT, "03-价值流图VSM详解.pptx") }).then(function() {
  console.log("?? 03-价值流图VSM详解.pptx created!");
}).catch(function(err) { console.error("Error:", err); });
