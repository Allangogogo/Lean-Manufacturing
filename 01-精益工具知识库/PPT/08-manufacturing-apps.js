const PptxGenJS = require("pptxgenjs");
const path = require("path");
const OUT = __dirname;

let pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.title = "制造工序应用 Manufacturing Process Applications";
pptx.author = "精益工具知识库";

const S = pptx.ShapeType;

const C = {
  P:  "1E2761",
  S:  "CADCFC",
  A:  "FFFFFF",
  L:  "F8FAFC",
  T:  "1E293B",
  TL: "64748B",
  G:  "059669",
  W:  "D97706",
  D:  "DC2626",
  TE: "0D9488",
  TL2:"5EEAD4",
};
const W = 13.33;
const H = 7.5;

function setBg(slide) { slide.background = { color: C.L }; }

function addTopBar(slide, color, barH) {
  barH = barH || 0.08;
  slide.addShape(S.rect, { x: 0, y: 0, w: W, h: barH, fill: { color: color }, line: { color: color } });
}

function addTitleBand(slide, title, subtitle) {
  var bandY = 0.08, bandH = 1.15;
  slide.addShape(S.rect, { x: 0, y: bandY, w: W, h: bandH, fill: { color: C.P }, line: { color: C.P } });
  slide.addText(title, { x: 0.6, y: bandY + 0.15, w: 12.13, h: 0.65, fontFace: "Microsoft YaHei", fontSize: 32, color: C.A, bold: true, valign: "middle" });
  if (subtitle) {
    slide.addText(subtitle, { x: 0.6, y: bandY + 0.72, w: 12.13, h: 0.4, fontFace: "Microsoft YaHei", fontSize: 14, color: C.S, valign: "middle" });
  }
}

function addFooter(slide, text) {
  var footH = 0.32, footY = H - footH;
  slide.addShape(S.rect, { x: 0, y: footY, w: W, h: footH, fill: { color: C.P }, line: { color: C.P } });
  slide.addText(text, { x: 0.5, y: footY + 0.02, w: 12.33, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 10, color: C.S, valign: "middle", align: "center" });
}

function sectLabel(slide, text) {
  slide.addShape(S.roundRect, { x: 0.6, y: 1.35, w: 2.4, h: 0.34, fill: { color: C.G }, rectRadius: 0.17, line: { color: C.G } });
  slide.addText(text, { x: 0.6, y: 1.35, w: 2.4, h: 0.34, fontFace: "Microsoft YaHei", fontSize: 12, color: C.A, bold: true, align: "center", valign: "middle" });
}

function cardB(slide, x, y, w, h, accent, items) {
  slide.addShape(S.rect, { x: x + 0.03, y: y + 0.04, w: w, h: h, fill: { color: "E2E8F0" }, line: { color: "000000" } });
  slide.addShape(S.rect, { x: x, y: y, w: w, h: h, fill: { color: C.A }, line: { color: "CBD5E1" } });
  slide.addShape(S.rect, { x: x, y: y, w: w, h: 0.06, fill: { color: accent }, line: { color: "000000" } });
  for (var i = 0; i < items.length; i++) {
    var it = items[i];
    slide.addText(it.t, { x: x + 0.15, y: y + (it.y || 0.12), w: w - 0.3, h: it.h || 0.4, fontFace: "Microsoft YaHei", fontSize: it.size || 10, color: it.color || C.T, bold: it.bold || false, valign: "middle" });
  }
}

function statCard(slide, x, y, number, unit, label, color) {
  slide.addShape(S.roundRect, { x: x, y: y, w: 2.8, h: 1.15, fill: { color: color || C.P }, rectRadius: 0.12, line: { color: color || C.P } });
  slide.addText(number + (unit || ""), { x: x, y: y + 0.12, w: 2.8, h: 0.55, fontFace: "Microsoft YaHei", fontSize: 28, color: C.A, bold: true, align: "center", valign: "middle" });
  slide.addText(label, { x: x, y: y + 0.65, w: 2.8, h: 0.4, fontFace: "Microsoft YaHei", fontSize: 10, color: C.A, align: "center", valign: "middle" });
}

function flowBox(slide, x, y, w, h, color, label, sublabel) {
  slide.addShape(S.roundRect, { x: x, y: y, w: w, h: h, fill: { color: color }, line: { color: color }, rectRadius: 0.12 });
  slide.addText(label, { x: x, y: y + 0.08, w: w, h: h * 0.55, fontFace: "Microsoft YaHei", fontSize: 11, color: C.A, bold: true, align: "center", valign: "middle" });
  if (sublabel) { slide.addText(sublabel, { x: x, y: y + h * 0.55, w: w, h: h * 0.4, fontFace: "Microsoft YaHei", fontSize: 8.5, color: C.A, align: "center", valign: "middle" }); }
}

function paramTag(slide, x, y, label, value, color) {
  slide.addShape(S.roundRect, { x: x, y: y, w: 1.5, h: 0.42, fill: { color: color }, rectRadius: 0.08, line: { color: color } });
  slide.addText(label, { x: x, y: y + 0.02, w: 1.5, h: 0.2, fontFace: "Microsoft YaHei", fontSize: 7, color: C.A, align: "center", valign: "middle" });
  slide.addText(value, { x: x, y: y + 0.18, w: 1.5, h: 0.22, fontFace: "Arial", fontSize: 9, color: C.A, bold: true, align: "center", valign: "middle" });
}

function th(slide, x, y, w, cols) {
  var tw = w[0] + w[1] + w[2];
  slide.addShape(S.rect, { x: x, y: y, w: tw, h: 0.44, fill: { color: C.P }, line: { color: C.P } });
  slide.addText(cols[0], { x: x, y: y, w: w[0], h: 0.44, fontFace: "Microsoft YaHei", fontSize: 11, color: C.A, bold: true, align: "center", valign: "middle" });
  slide.addText(cols[1], { x: x + w[0], y: y, w: w[1], h: 0.44, fontFace: "Microsoft YaHei", fontSize: 11, color: C.A, bold: true, align: "center", valign: "middle" });
  slide.addText(cols[2], { x: x + w[0] + w[1], y: y, w: w[2], h: 0.44, fontFace: "Microsoft YaHei", fontSize: 11, color: C.A, bold: true, align: "center", valign: "middle" });
}

function tr(slide, x, y, w, row, bg, c1, c2, c3) {
  var tw = w[0] + w[1] + w[2];
  slide.addShape(S.rect, { x: x, y: y, w: tw, h: 0.42, fill: { color: bg }, line: { color: "CBD5E1" } });
  slide.addText(row[0], { x: x, y: y, w: w[0], h: 0.42, fontFace: "Microsoft YaHei", fontSize: 10, color: c1, align: "center", valign: "middle" });
  slide.addText(row[1], { x: x + w[0], y: y, w: w[1], h: 0.42, fontFace: "Microsoft YaHei", fontSize: 10, color: c2, align: "center", valign: "middle" });
  slide.addText(row[2], { x: x + w[0] + w[1], y: y, w: w[2], h: 0.42, fontFace: "Microsoft YaHei", fontSize: 10, color: c3, align: "center", valign: "middle" });
}

function th4(slide, x, y, w, cols) {
  var tw = w[0] + w[1] + w[2] + w[3];
  slide.addShape(S.rect, { x: x, y: y, w: tw, h: 0.44, fill: { color: C.P }, line: { color: C.P } });
  slide.addText(cols[0], { x: x, y: y, w: w[0], h: 0.44, fontFace: "Microsoft YaHei", fontSize: 11, color: C.A, bold: true, align: "center", valign: "middle" });
  slide.addText(cols[1], { x: x + w[0], y: y, w: w[1], h: 0.44, fontFace: "Microsoft YaHei", fontSize: 11, color: C.A, bold: true, align: "center", valign: "middle" });
  slide.addText(cols[2], { x: x + w[0] + w[1], y: y, w: w[2], h: 0.44, fontFace: "Microsoft YaHei", fontSize: 11, color: C.A, bold: true, align: "center", valign: "middle" });
  slide.addText(cols[3], { x: x + w[0] + w[1] + w[2], y: y, w: w[3], h: 0.44, fontFace: "Microsoft YaHei", fontSize: 11, color: C.A, bold: true, align: "center", valign: "middle" });
}

function tr4(slide, x, y, w, row, bg, c1, c2, c3, c4) {
  var tw = w[0] + w[1] + w[2] + w[3];
  slide.addShape(S.rect, { x: x, y: y, w: tw, h: 0.42, fill: { color: bg }, line: { color: "CBD5E1" } });
  slide.addText(row[0], { x: x, y: y, w: w[0], h: 0.42, fontFace: "Microsoft YaHei", fontSize: 9, color: c1, align: "center", valign: "middle" });
  slide.addText(row[1], { x: x + w[0], y: y, w: w[1], h: 0.42, fontFace: "Microsoft YaHei", fontSize: 9, color: c2, align: "center", valign: "middle" });
  slide.addText(row[2], { x: x + w[0] + w[1], y: y, w: w[2], h: 0.42, fontFace: "Microsoft YaHei", fontSize: 9, color: c3, align: "center", valign: "middle" });
  slide.addText(row[3], { x: x + w[0] + w[1] + w[2], y: y, w: w[3], h: 0.42, fontFace: "Microsoft YaHei", fontSize: 9, color: c4, align: "center", valign: "middle" });
}

// ============================================================
// SLIDE 01: Chapter Cover
// ============================================================
(function(){
  var s = pptx.addSlide();
  s.background = { color: C.P };
  s.addShape(S.ellipse, { x: 9.5, y: -1.5, w: 6.5, h: 6.5, fill: { color: "1B2D6B" }, line: { color: "000000" } });
  s.addShape(S.ellipse, { x: 10.5, y: -0.5, w: 4.5, h: 4.5, fill: { color: "233B7A" }, line: { color: "000000" } });
  s.addText("08", { x: 0.8, y: 1, w: 4, h: 2.8, fontFace: "Arial", fontSize: 100, color: C.S, bold: true });
  s.addShape(S.rect, { x: 0.8, y: 3.6, w: 3.2, h: 0.06, fill: { color: C.G }, line: { color: "000000" } });
  s.addText("制造工序应用", { x: 0.8, y: 3.8, w: 8.5, h: 1.2, fontFace: "Microsoft YaHei", fontSize: 44, color: C.A, bold: true, valign: "middle" });
  s.addText("Manufacturing Process Applications", { x: 0.8, y: 4.65, w: 8, h: 0.6, fontFace: "Arial", fontSize: 20, color: C.S });
  s.addText("精益工具在制造中的全面应用\n从机加工到包装的端到端改善实践", { x: 0.8, y: 5.45, w: 8, h: 1, fontFace: "Microsoft YaHei", fontSize: 14, color: C.TL });
})();

// ============================================================
// SLIDE 02: Manufacturing Process Overview
// ============================================================
(function(){
  var s = pptx.addSlide();
  setBg(s);
  addTopBar(s, C.TE);
  addTitleBand(s, "制造流程概览", "Discrete Manufacturing Process Overview");
  addFooter(s, "08 | 制造工序应用 | 制造流程概览");
  sectLabel(s, "端到端流程 · 关键参数");

  var processes = [
    { n: "机加工", e: "Machining", c: C.P, ct: "0.5-2s/件", oee: "75-85%", defect: "<0.5%" },
    { n: "精加工", e: "Precision Machining", c: C.G, ct: "0.3-1s/件", oee: "80-90%", defect: "<0.3%" },
    { n: "热处理", e: "Heat Treatment", c: C.W, ct: "2-4h/炉", oee: "70-80%", defect: "<0.2%" },
    { n: "表面处理", e: "Surface Treatment", c: C.TE, ct: "30-90min", oee: "65-75%", defect: "<1.0%" },
    { n: "装配", e: "Sorting", c: "636F85", ct: "实时", oee: "95-98%", defect: "<0.1%" },
    { n: "包装", e: "Packing", c: "8B5CF6", ct: "实时", oee: "85-92%", defect: "<0.05%" },
  ];

  var bw = 1.65, bh = 1.75, gap = 0.15;
  var totalW = processes.length * bw + (processes.length - 1) * gap;
  var startX = (W - totalW) / 2;
  var startY = 1.85;

  for (var i = 0; i < processes.length; i++) {
    var p = processes[i];
    var x = startX + i * (bw + gap);
    flowBox(s, x, startY, bw, bh, p.c, p.n, p.e);
    var tagY = startY + bh + 0.08;
    paramTag(s, x, tagY, "CT", p.ct, p.c);
    paramTag(s, x + bw / 2 + 0.08, tagY, "OEE", p.oee, "1A3A5C");
    s.addText("不良率: " + p.defect, { x: x, y: tagY + 0.46, w: bw, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 7.5, color: C.D, align: "center", valign: "middle" });
    if (i < processes.length - 1) {
      s.addShape(S.rightArrow, { x: x + bw + 0.02, y: startY + bh / 2 - 0.15, w: gap - 0.04, h: 0.3, fill: { color: C.TL }, line: { color: C.TL } });
    }
  }

  s.addShape(S.rect, { x: 0.5, y: 4.4, w: 12.33, h: 0.06, fill: { color: C.TE }, line: { color: "000000" } });
  s.addText("端到端关键指标总览", { x: 0.5, y: 4.5, w: 12.33, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 10, color: C.TL, align: "center", valign: "middle" });

  statCard(s, 1.0, 4.9, "62", "s", "单件总CT（不含炉）", C.P);
  statCard(s, 4.2, 4.9, "78", "%", "综合OEE目标", C.G);
  statCard(s, 7.4, 4.9, "<2", "%", "综合不良率目标", C.TE);
  statCard(s, 10.6, 4.9, "14", "天", "交期改善目标", C.W);
})();

// ============================================================
// SLIDE 03: Machining Lean Applications
// ============================================================
(function(){
  var s = pptx.addSlide();
  setBg(s);
  addTopBar(s, C.G);
  addTitleBand(s, "机加工工序精益应用", "Machining — SMED · TPM · Poka-Yoke");
  addFooter(s, "08 | 制造工序应用 | 机加工工序精益应用");
  sectLabel(s, "PART 1 · 机加工");

  cardB(s, 0.5, 1.78, 3.8, 2.55, C.G, [
    { t: "SMED 快速换模", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 换模时间：60min -> <10min", y: 0.42, size: 10, color: C.T },
    { t: "· 标准化工装夹具，模具预热外移", y: 0.72, size: 10, color: C.T },
    { t: "· 参数预存一键调用", y: 1.02, size: 10, color: C.T },
    { t: "效果：换模频次 1次/日 -> 3次/日", y: 1.38, size: 10, bold: true, color: C.G },
    { t: "Die change: 60min -> <10min | Frequency: 1x->3x/day", y: 2.05, size: 8, color: C.TL }
  ]);

  cardB(s, 0.5, 4.53, 3.8, 2.2, C.TE, [
    { t: "TPM 多工位冲床维护", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 自主保全：操作员日常点检", y: 0.42, size: 10, color: C.T },
    { t: "· 计划保全：预测性维护系统", y: 0.72, size: 10, color: C.T },
    { t: "· OEE目标：从65%提升至85%", y: 1.02, size: 10, color: C.T },
    { t: "· 关键备件安全库存管理", y: 1.32, size: 10, color: C.T },
    { t: "OEE: 65% -> 85% | Unplanned downtime: -70%", y: 1.85, size: 8, color: C.TL }
  ]);

  cardB(s, 4.6, 1.78, 3.8, 2.55, C.W, [
    { t: "Poka-Yoke 防错应用", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 错误模具检测：定位销+接近传感器", y: 0.42, size: 10, color: C.T },
    { t: "· 材料线径超差：激光测径自动停机", y: 0.72, size: 10, color: C.T },
    { t: "· 短料检测：缺料自动报警", y: 1.02, size: 10, color: C.T },
    { t: "· 产品漏冲：重量检测自动剔除", y: 1.32, size: 10, color: C.T },
    { t: "Zero defect since 2022 | 100% auto detection", y: 2.05, size: 8, color: C.TL }
  ]);

  var tx = 8.7, tw = [2.0, 2.0, 2.33];
  th(s, tx, 1.78, tw, ["关键指标", "改善前", "改善后"]);
  var rows3 = [
    ["Cycle Time", "2.0s", "0.8s"],
    ["模具寿命", "5万件", "8万件"],
    ["材料利用率", "82%", "93%"],
    ["换模时间", "60min", "<10min"],
    ["OEE", "65%", "85%"],
    ["不良率", "1.2%", "0.3%"],
  ];
  for (var i = 0; i < rows3.length; i++) {
    var bg = i % 2 === 0 ? C.A : C.L;
    tr(s, tx, 2.22 + i * 0.44, tw, rows3[i], bg, C.T, C.T, C.G);
  }

  s.addShape(S.roundRect, { x: 4.6, y: 4.53, w: 8.23, h: 0.55, fill: { color: "ECFDF5" }, rectRadius: 0.1, line: { color: C.G } });
  s.addText("机加工是制造第一道关键工序——SMED释放产能、TPM稳定设备、Poka-Yoke杜绝批量不良", { x: 4.6, y: 4.53, w: 8.23, h: 0.55, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.T, align: "center", valign: "middle" });
})();

// ============================================================
// SLIDE 04: Precision Machining Lean Applications
// ============================================================
(function(){
  var s = pptx.addSlide();
  setBg(s);
  addTopBar(s, C.G);
  addTitleBand(s, "精加工工序精益应用", "Precision Machining — Roller Life · SPC · Quick Change");
  addFooter(s, "08 | 制造工序应用 | 精加工工序精益应用");
  sectLabel(s, "PART 2 · 精加工");

  cardB(s, 0.5, 1.78, 4.0, 2.2, C.G, [
    { t: "丝辊寿命管理", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 建立丝辊寿命预测模型", y: 0.42, size: 10, color: C.T },
    { t: "· 每班记录加工件数，提前预警更换", y: 0.72, size: 10, color: C.T },
    { t: "· 丝辊平均寿命：从8万件提升至12万件", y: 1.02, size: 10, color: C.T },
    { t: "Roller life: 80K -> 120K pcs | Scrap rate -60%", y: 1.65, size: 8, color: C.TL }
  ]);

  cardB(s, 0.5, 4.18, 4.0, 2.1, C.TE, [
    { t: "轮廓 SPC 管控", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 量规抽检频率：首件+每30min", y: 0.42, size: 10, color: C.T },
    { t: "· 关键尺寸实时SPC趋势图监控", y: 0.72, size: 10, color: C.T },
    { t: "· CPK目标：>= 1.67（关键特性）", y: 1.02, size: 10, color: C.T },
    { t: "SPC CPK >= 1.67 | Profile auto inspection", y: 1.65, size: 8, color: C.TL }
  ]);

  cardB(s, 4.8, 1.78, 4.0, 2.2, C.W, [
    { t: "快速换辊 Quick Roller Change", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 应用SMED：从45min降至8min", y: 0.42, size: 10, color: C.T },
    { t: "· 标准化工装夹具设计", y: 0.72, size: 10, color: C.T },
    { t: "· 换辊参数预存，一键恢复", y: 1.02, size: 10, color: C.T },
    { t: "Roller change: 45min -> 8min | Setup time -82%", y: 1.65, size: 8, color: C.TL }
  ]);

  cardB(s, 4.8, 4.18, 4.0, 2.1, C.D, [
    { t: "目视化管理 Visual Management", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 产量/质量实时看板（Andon）", y: 0.42, size: 10, color: C.T },
    { t: "· 丝辊更换倒计时可视化", y: 0.72, size: 10, color: C.T },
    { t: "· 缺陷样品展示板——对比良品/NG品", y: 1.02, size: 10, color: C.T },
    { t: "Andon response < 30s | Visual QC board on-site", y: 1.65, size: 8, color: C.TL }
  ]);

  var tx = 9.1, tw = [2.0, 2.0, 2.0];
  th(s, tx, 1.78, tw, ["改善项目", "改善前", "改善后"]);
  var rows4 = [
    ["换辊时间", "45min", "8min"],
    ["丝辊寿命", "8万件", "12万件"],
    ["尺寸不良率", "0.8%", "0.2%"],
    ["SPC CPK", "1.2", "1.75"],
  ];
  for (var i = 0; i < rows4.length; i++) {
    var bg = i % 2 === 0 ? C.A : C.L;
    tr(s, tx, 2.22 + i * 0.44, tw, rows4[i], bg, C.T, C.T, C.G);
  }
})();

// ============================================================
// SLIDE 05: Heat Treatment Lean Applications
// ============================================================
(function(){
  var s = pptx.addSlide();
  setBg(s);
  addTopBar(s, C.W);
  addTitleBand(s, "热处理工序精益应用", "Heat Treatment — CQI-9 · Energy Efficiency · TPM");
  addFooter(s, "08 | 制造工序应用 | 热处理工序精益应用");
  sectLabel(s, "PART 3 · 热处理");

  cardB(s, 0.5, 1.78, 3.8, 2.2, C.W, [
    { t: "炉装量优化 Loading Optimization", y: 0.08, size: 11, bold: true, color: C.P },
    { t: "· 标准化装料方式与层间距", y: 0.42, size: 10, color: C.T },
    { t: "· 装炉量从80%提升至95%有效利用", y: 0.72, size: 10, color: C.T },
    { t: "· 减少空炉运行，年省电费约15万元", y: 1.02, size: 10, color: C.T },
    { t: "Furnace utilization: 80% -> 95%", y: 1.65, size: 8, color: C.TL }
  ]);

  cardB(s, 0.5, 4.18, 3.8, 2.5, C.TE, [
    { t: "温度均匀性 SOP & 能耗改善", y: 0.08, size: 11, bold: true, color: C.P },
    { t: "· 炉内温度均匀性测试（TUS）定期验证", y: 0.38, size: 9.5, color: C.T },
    { t: "· 热电偶校准周期标准化", y: 0.65, size: 9.5, color: C.T },
    { t: "· 余热回收系统：预热进料原材料", y: 0.92, size: 9.5, color: C.T },
    { t: "· 天然气单耗从85降至68 m³/吨", y: 1.19, size: 9.5, color: C.T },
    { t: "Gas consumption: 85 -> 68 m3/ton | Energy cost -20%", y: 1.8, size: 8, color: C.TL }
  ]);

  cardB(s, 4.6, 1.78, 3.8, 2.2, C.G, [
    { t: "CQI-9 合规管理", y: 0.08, size: 11, bold: true, color: C.P },
    { t: "· 过程失效模式分析（PFMEA）体系", y: 0.42, size: 10, color: C.T },
    { t: "· 炉温记录系统连续监控+报警", y: 0.72, size: 10, color: C.T },
    { t: "· 年度过程审核确保体系有效运行", y: 1.02, size: 10, color: C.T },
    { t: "CQI-9 compliant | Zero process audit finding", y: 1.65, size: 8, color: C.TL }
  ]);

  cardB(s, 4.6, 4.18, 3.8, 2.5, C.P, [
    { t: "TPM 炉体维护", y: 0.08, size: 11, bold: true, color: C.P },
    { t: "· 炉膛清扫周期：每周一次标准化", y: 0.38, size: 9.5, color: C.T },
    { t: "· 网带寿命管理：定期张力检测", y: 0.65, size: 9.5, color: C.T },
    { t: "· 气氛碳势控制系统预防性校验", y: 0.92, size: 9.5, color: C.T },
    { t: "· 计划停机维护时间缩短40%", y: 1.19, size: 9.5, color: C.T },
    { t: "Planned maintenance time -40% | Belt life +30%", y: 1.8, size: 8, color: C.TL }
  ]);

  s.addShape(S.ellipse, { x: 9.8, y: 3.5, w: 2.0, h: 1.0, fill: { color: C.W }, line: { color: C.W } });
  s.addText("年综合\n节能约\n20%", { x: 9.8, y: 3.5, w: 2.0, h: 1.0, fontFace: "Microsoft YaHei", fontSize: 12, color: C.A, bold: true, align: "center", valign: "middle" });
})();

// ============================================================
// SLIDE 06: Surface Treatment Lean Applications
// ============================================================
(function(){
  var s = pptx.addSlide();
  setBg(s);
  addTopBar(s, C.TE);
  addTitleBand(s, "表面处理工序精益应用", "Surface Treatment — Coating Control · WIP Reduction");
  addFooter(s, "08 | 制造工序应用 | 表面处理精益应用");
  sectLabel(s, "PART 4 · 表面处理");

  cardB(s, 0.5, 1.78, 3.8, 2.55, C.TE, [
    { t: "镀液化学控制", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 镀液成分自动分析+补加系统", y: 0.42, size: 10, color: C.T },
    { t: "· pH值/温度/电流密度实时监控", y: 0.72, size: 10, color: C.T },
    { t: "· 镀层厚度CPK从1.0提升至1.67", y: 1.02, size: 10, color: C.T },
    { t: "· 镀液异常自动报警+停机保护", y: 1.32, size: 10, color: C.T },
    { t: "Coating thickness CPK: 1.0 -> 1.67 | Auto dosing", y: 2.05, size: 8, color: C.TL }
  ]);

  cardB(s, 0.5, 4.53, 3.8, 2.2, C.G, [
    { t: "挂具/滚筒优化", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 挂具设计优化：装载量+20%", y: 0.42, size: 10, color: C.T },
    { t: "· 滚筒转速/倾斜角DOE优化", y: 0.72, size: 10, color: C.T },
    { t: "· 挂具定期清洗/退镀标准化", y: 1.02, size: 10, color: C.T },
    { t: "Loading capacity +20% | Barrel efficiency +15%", y: 1.65, size: 8, color: C.TL }
  ]);

  cardB(s, 4.6, 1.78, 3.8, 2.55, C.W, [
    { t: "环保合规 Environmental Compliance", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 废水在线监测：pH/Cr6+/Ni2+实时", y: 0.42, size: 10, color: C.T },
    { t: "· 化学品存储双人双锁管理", y: 0.72, size: 10, color: C.T },
    { t: "· 危废分类收集+台账追溯", y: 1.02, size: 10, color: C.T },
    { t: "· 年度环保审计零不符合项", y: 1.32, size: 10, color: C.T },
    { t: "Zero environmental violation | Online monitoring", y: 2.05, size: 8, color: C.TL }
  ]);

  // WIP reduction section
  s.addText("镀后至包装 WIP 削减", { x: 4.6, y: 4.53, w: 4.0, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 12, color: C.P, bold: true, valign: "middle" });

  var wipBefore = [
    { label: "电镀后\n暂存", time: "4h", c: C.D },
    { label: "钝化后\n晾干", time: "2h", c: C.W },
    { label: "等待\n装配", time: "6h", c: C.D },
    { label: "等待\n包装", time: "8h", c: C.W },
  ];
  var wipAfter = [
    { label: "连续流\n水线", time: "0.5h", c: C.G },
    { label: "在线\n干燥", time: "0.2h", c: C.TE },
    { label: "自动\n装配", time: "0.1h", c: C.G },
    { label: "即时\n包装", time: "0.2h", c: C.TE },
  ];

  var wipX = 4.6;
  for (var i = 0; i < wipBefore.length; i++) {
    var wb = wipBefore[i];
    s.addShape(S.roundRect, { x: wipX + i * 1.05, y: 4.9, w: 0.95, h: 0.65, fill: { color: wb.c }, rectRadius: 0.08, line: { color: wb.c } });
    s.addText(wb.label, { x: wipX + i * 1.05, y: 4.9, w: 0.95, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 7, color: C.A, align: "center", valign: "middle" });
    s.addText(wb.time, { x: wipX + i * 1.05, y: 5.2, w: 0.95, h: 0.25, fontFace: "Arial", fontSize: 9, color: C.A, bold: true, align: "center", valign: "middle" });
  }
  s.addText("改善前 WIP: 20h", { x: wipX, y: 5.6, w: 4.2, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 9, color: C.D, bold: true, align: "center" });

  var wipX2 = 9.1;
  for (var i = 0; i < wipAfter.length; i++) {
    var wa = wipAfter[i];
    s.addShape(S.roundRect, { x: wipX2 + i * 1.05, y: 4.9, w: 0.95, h: 0.65, fill: { color: wa.c }, rectRadius: 0.08, line: { color: wa.c } });
    s.addText(wa.label, { x: wipX2 + i * 1.05, y: 4.9, w: 0.95, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 7, color: C.A, align: "center", valign: "middle" });
    s.addText(wa.time, { x: wipX2 + i * 1.05, y: 5.2, w: 0.95, h: 0.25, fontFace: "Arial", fontSize: 9, color: C.A, bold: true, align: "center", valign: "middle" });
  }
  s.addText("改善后 WIP: 1h", { x: wipX2, y: 5.6, w: 4.2, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 9, color: C.G, bold: true, align: "center" });

  s.addShape(S.rightArrow, { x: 8.85, y: 5.05, w: 0.22, h: 0.35, fill: { color: C.G }, line: { color: C.G } });
})();

// ============================================================
// SLIDE 07: Packaging Lean Applications
// ============================================================
(function(){
  var s = pptx.addSlide();
  setBg(s);
  addTopBar(s, "8B5CF6");
  addTitleBand(s, "包装工序精益应用", "Packaging — Poka-Yoke · Kanban · Line Balance");
  addFooter(s, "08 | 制造工序应用 | 包装工序精益应用");
  sectLabel(s, "PART 5 · 包装");

  cardB(s, 0.5, 1.78, 3.8, 2.55, "8B5CF6", [
    { t: "混品防止 Poka-Yoke", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 称重扫码双重校验系统", y: 0.42, size: 10, color: C.A },
    { t: "· 自动称重精度：+-0.1g", y: 0.72, size: 10, color: C.A },
    { t: "· 条码/RFID追溯系统联动", y: 1.02, size: 10, color: C.A },
    { t: "· 混装次数：从年均12次降至0次", y: 1.32, size: 10, color: C.A },
    { t: "Mix-up prevention: 0 incidents since 2022", y: 2.05, size: 8, color: C.A }
  ]);

  cardB(s, 4.6, 1.78, 3.8, 2.55, C.G, [
    { t: "纸箱标准化 Carton Standardization", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 纸箱规格从23种缩减至8种", y: 0.42, size: 10, color: C.T },
    { t: "· 内衬/隔板通用化设计", y: 0.72, size: 10, color: C.T },
    { t: "· 包材采购成本降低25%", y: 1.02, size: 10, color: C.T },
    { t: "· 库存空间减少40%", y: 1.32, size: 10, color: C.T },
    { t: "Carton SKUs: 23 -> 8 | Procurement cost -25%", y: 2.05, size: 8, color: C.TL }
  ]);

  cardB(s, 8.7, 1.78, 4.13, 2.55, C.TE, [
    { t: "包材看板 Kanban for Packaging", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "· 双箱看板系统触发包材补充", y: 0.42, size: 10, color: C.T },
    { t: "· 安全库存自动计算(ERP联动)", y: 0.72, size: 10, color: C.T },
    { t: "· 缺料停线风险降低90%", y: 1.02, size: 10, color: C.T },
    { t: "· 包材周转天数从15天降至5天", y: 1.32, size: 10, color: C.T },
    { t: "Kanban system | Stockout risk -90%", y: 2.05, size: 8, color: C.TL }
  ]);

  // Line balance section
  s.addText("产线平衡优化 Line Balance", { x: 0.5, y: 4.6, w: 5.0, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 12, color: C.P, bold: true, valign: "middle" });

  // Before line balance chart
  var stations = ["称重", "装袋", "装箱", "封箱", "贴标", "码垛"];
  var beforeTimes = [12, 18, 15, 10, 8, 14];
  var afterTimes = [12, 13, 13, 11, 9, 12];

  var maxTime = 20;
  var barMaxW = 2.5;
  var barH = 0.32;
  var bX = 0.5, bY = 4.95;

  s.addText("改善前 CT", { x: bX, y: bY - 0.25, w: 1.5, h: 0.22, fontFace: "Microsoft YaHei", fontSize: 8, color: C.D });
  s.addText("改善后 CT", { x: bX + 4.5, y: bY - 0.25, w: 1.5, h: 0.22, fontFace: "Microsoft YaHei", fontSize: 8, color: C.G });

  for (var i = 0; i < stations.length; i++) {
    var sy = bY + i * (barH + 0.05);
    var bw1 = (beforeTimes[i] / maxTime) * barMaxW;
    var bw2 = (afterTimes[i] / maxTime) * barMaxW;

    s.addText(stations[i], { x: bX + 2.6, y: sy, w: 0.7, h: barH, fontFace: "Microsoft YaHei", fontSize: 8, color: C.T, align: "right", valign: "middle" });

    s.addShape(S.rect, { x: bX + 3.4, y: sy, w: bw1, h: barH, fill: { color: "FEE2E2" }, line: { color: "000000" } });
    s.addShape(S.rect, { x: bX + 3.4, y: sy, w: bw1, h: barH, fill: { color: C.D }, line: { color: "000000" } });
    s.addText(beforeTimes[i] + "s", { x: bX + 3.4, y: sy, w: bw1, h: barH, fontFace: "Arial", fontSize: 7, color: C.A, align: "center", valign: "middle" });

    s.addShape(S.rect, { x: bX + 3.4 + barMaxW + 0.1, y: sy, w: bw2, h: barH, fill: { color: C.G }, line: { color: "000000" } });
    s.addText(afterTimes[i] + "s", { x: bX + 3.4 + barMaxW + 0.1, y: sy, w: bw2, h: barH, fontFace: "Arial", fontSize: 7, color: C.A, align: "center", valign: "middle" });
  }

  // Line balance rate
  s.addShape(S.ellipse, { x: 9.0, y: 5.0, w: 2.2, h: 1.0, fill: { color: C.G }, line: { color: C.G } });
  s.addText("产线平衡率\n68% -> 88%", { x: 9.0, y: 5.0, w: 2.2, h: 1.0, fontFace: "Microsoft YaHei", fontSize: 12, color: C.A, bold: true, align: "center", valign: "middle" });
})();

// ============================================================
// SLIDE 08: Comprehensive Improvement Case Study
// ============================================================
(function(){
  var s = pptx.addSlide();
  setBg(s);
  addTopBar(s, C.P);
  addTitleBand(s, "综合改善案例", "Comprehensive Improvement Case — Before / After All Processes");
  addFooter(s, "08 | 制造工序应用 | 综合改善案例");
  sectLabel(s, "全流程改善成效");

  // Top row: key improvement stats
  statCard(s, 0.5, 1.78, "62", "% -> 85%", "OEE 设备综合效率", C.G);
  statCard(s, 3.5, 1.78, "14", "天 -> 5天", "交货周期改善", C.TE);
  statCard(s, 6.5, 1.78, "3.2", "% -> 0.8%", "综合不良率下降", C.P);
  statCard(s, 9.5, 1.78, "28", "天 -> 8天", "在制品库存天数", C.W);

  // Detailed process improvement table
  var tx = 0.5, tw = [2.0, 2.8, 2.8, 2.8, 2.0];
  th4(s, tx, 3.15, tw, ["工序", "改善前", "改善后", "关键工具", "改善幅度"]);

  var caseRows = [
    ["机加工", "OEE 65%\n换模 60min", "OEE 85%\n换模 <10min", "SMED\nTPM\nPoka-Yoke", "换模 -83%"],
    ["精加工", "换辊 45min\n不良 0.8%", "换辊 8min\n不良 0.2%", "SMED\nSPC\n目视管理", "不良 -75%"],
    ["热处理", "能耗 85m³/吨\n装量 80%", "能耗 68m³/吨\n装量 95%", "CQI-9\nTPM\nSOP", "能耗 -20%"],
    ["表面处理", "WIP 20h\n膜厚CPK 1.0", "WIP 1h\n膜厚CPK 1.67", "自动化\nSPC\n连续流", "WIP -95%"],
    ["装配", "人工目检\n漏检率 2%", "自动光学装配\n漏检率 <0.1%", "AOI\nPoka-Yoke\n自动化", "漏检 -95%"],
    ["包装", "混装12次/年\n平衡率 68%", "混装 0次/年\n平衡率 88%", "Poka-Yoke\n看板\n线平衡", "混装归零"],
  ];

  for (var i = 0; i < caseRows.length; i++) {
    var bg = i % 2 === 0 ? C.A : C.L;
    tr4(s, tx, 3.59 + i * 0.56, tw, caseRows[i], bg, C.T, C.T, C.T, C.G, C.G);
  }

  // Bottom highlight
  s.addShape(S.rect, { x: 0.5, y: 7.05, w: 12.33, h: 0.06, fill: { color: C.P }, line: { color: "000000" } });
  s.addShape(S.roundRect, { x: 2.5, y: 6.75, w: 8.33, h: 0.55, fill: { color: "1E2761" }, rectRadius: 0.1, line: { color: C.G } });
  s.addText("综合改善成果：年节省约 480 万元 | 客户投诉率下降 80% | 准时交付率 98.5%", { x: 2.5, y: 6.75, w: 8.33, h: 0.55, fontFace: "Microsoft YaHei", fontSize: 11, color: C.A, bold: true, align: "center", valign: "middle" });
})();

// ============================================================
// OUTPUT
// ============================================================
pptx.writeFile({ fileName: path.join(OUT, "08-制造工序应用.pptx") })
  .then(function() { console.log("OK: 08-制造工序应用.pptx created"); })
  .catch(function(err) { console.error("ERR:", err); process.exit(1); });
