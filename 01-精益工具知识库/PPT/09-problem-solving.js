const PptxGenJS = require("pptxgenjs");
const path = require("path");
const OUT = __dirname;

let pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.title = "问题解决方法 5 Problem-Solving Methods";
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
  slide.addShape(S.roundRect, { x: 0.6, y: 1.35, w: 3.0, h: 0.34, fill: { color: C.G }, rectRadius: 0.17, line: { color: C.G } });
  slide.addText(text, { x: 0.6, y: 1.35, w: 3.0, h: 0.34, fontFace: "Microsoft YaHei", fontSize: 12, color: C.A, bold: true, align: "center", valign: "middle" });
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

// ===== SLIDE 01: Cover =====
(function(){
  var s = pptx.addSlide();
  s.background = { color: C.P };
  s.addShape(S.ellipse, { x: 9.5, y: -1.5, w: 6.5, h: 6.5, fill: { color: "1B2D6B" }, line: { color: "000000" } });
  s.addShape(S.ellipse, { x: 10.5, y: -0.5, w: 4.5, h: 4.5, fill: { color: "233B7A" }, line: { color: "000000" } });
  s.addText("09", { x: 0.8, y: 1, w: 4, h: 2.8, fontFace: "Arial", fontSize: 100, color: C.S, bold: true });
  s.addShape(S.rect, { x: 0.8, y: 3.6, w: 3.2, h: 0.06, fill: { color: C.G }, line: { color: "000000" } });
  s.addText("问题解决方法", { x: 0.8, y: 3.8, w: 8.5, h: 1.2, fontFace: "Microsoft YaHei", fontSize: 44, color: C.A, bold: true, valign: "middle" });
  s.addText("5 Problem-Solving Methods", { x: 0.8, y: 4.65, w: 8, h: 0.6, fontFace: "Arial", fontSize: 20, color: C.S });
  s.addText("Gemba Walk | A3 报告 | PDCA 循环 | DMAIC | VA/VE\n连接件制造精益问题解决利器", { x: 0.8, y: 5.45, w: 8, h: 1, fontFace: "Microsoft YaHei", fontSize: 14, color: C.TL });
})();

// ===== SLIDE 02: Gemba Walk =====
(function(){
  var s = pptx.addSlide();
  setBg(s); addTopBar(s, C.G); addTitleBand(s, "Gemba Walk 现场走动", "Go to the Real Place & See the Real Thing"); addFooter(s, "09 | 问题解决方法 | Gemba Walk");
  sectLabel(s, "PART 1 · 现场走动");

  cardB(s, 0.5, 1.78, 5.8, 1.55, C.G, [
    { t: "什么是 Gemba Walk？", y: 0.08, size: 13, bold: true, color: C.P },
    { t: "Gemba（现场）= 真正发生工作的地点", y: 0.42, size: 10.5, color: C.T },
    { t: "管理者亲临现场，观察实际流程、\n与员工交流、发现浪费与问题", y: 0.72, size: 10, color: C.TL },
    { t: "核心理念：问题在现场，答案也在现场", y: 1.08, size: 10, bold: true, color: C.G },
  ]);

  cardB(s, 6.8, 1.78, 6.03, 1.55, C.TE, [
    { t: "如何有效开展 Gemba Walk", y: 0.08, size: 13, bold: true, color: C.P },
    { t: "1. 制定走动路线与频次计划", y: 0.42, size: 10, color: C.T },
    { t: "2. 带着问题意识去观察（不预设结论）", y: 0.68, size: 10, color: C.T },
    { t: "3. 多提问、少指责（Why? How? What if?）", y: 0.94, size: 10, color: C.T },
    { t: "4. 记录观察结果，立即制定对策", y: 1.20, size: 10, color: C.T },
  ]);

  // 5 focus area cards
  var focuses = [
    { t: "安全 Safety", d: "违章操作\nPPE佩戴\n设备保护", c: C.D },
    { t: "质量 Quality", d: "首件检查\n缺陷流出\n标准执行", c: C.W },
    { t: "效率 Efficiency", d: "人机等待\n动作浪费\n产能瓶颈", c: C.G },
    { t: "设备 Equipment", d: "稼动状况\n点检记录\n异常信号", c: C.TE },
    { t: "人员 People", d: "技能水平\n工作状态\n5S执行", c: C.P },
  ];
  var cw = 2.4, cx0 = 0.5;
  for (var i = 0; i < focuses.length; i++) {
    var f = focuses[i];
    var x = cx0 + i * (cw + 0.13);
    s.addShape(S.roundRect, { x: x, y: 3.55, w: cw, h: 1.55, fill: { color: f.c }, rectRadius: 0.1, line: { color: f.c } });
    s.addText(f.t, { x: x, y: 3.65, w: cw, h: 0.4, fontFace: "Microsoft YaHei", fontSize: 12, color: C.A, bold: true, align: "center", valign: "middle" });
    s.addText(f.d, { x: x, y: 4.05, w: cw, h: 0.95, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.A, align: "center", valign: "middle" });
  }

  // Checklist
  s.addText("Gemba Walk 观察清单（连接件工厂专用）", { x: 0.5, y: 5.25, w: 7, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 12, color: C.P, bold: true, valign: "middle" });
  var checks = [
    "冷镦机首件检验记录是否按时填写？",
    "攻牙工序是否有漏攻防错装置？",
    "热处理炉温监控是否在标准范围内？",
    "包装工位称重扫码系统是否正常？",
    "操作员是否按标准作业顺序执行？",
    "周转料架是否超过最大容量限制？"
  ];
  for (var j = 0; j < checks.length; j++) {
    var col = j < 3 ? 0.5 : 6.9;
    var ry = 5.6 + (j % 3) * 0.42;
    s.addShape(S.roundRect, { x: col, y: ry, w: 0.3, h: 0.28, fill: { color: C.G }, rectRadius: 0.06, line: { color: C.G } });
    s.addText("OK", { x: col, y: ry, w: 0.3, h: 0.28, fontFace: "Arial", fontSize: 10, color: C.A, align: "center", valign: "middle", bold: true });
    s.addText(checks[j], { x: col + 0.38, y: ry, w: 5.7, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.T, valign: "middle" });
  }
})();

// ===== SLIDE 03: A3 Problem Solving =====
(function(){
  var s = pptx.addSlide();
  setBg(s); addTopBar(s, C.P); addTitleBand(s, "A3 问题解决法", "One-Page Thinking & Structured Problem Solving"); addFooter(s, "09 | 问题解决方法 | A3 问题解决法");
  sectLabel(s, "PART 2 · A3 报告");

  var a3x = 0.8, a3y = 1.85, a3w = 11.73;
  s.addShape(S.rect, { x: a3x, y: a3y, w: a3w, h: 0.44, fill: { color: C.P }, line: { color: C.P } });
  s.addText("A3 问题解决报告模板", { x: a3x, y: a3y, w: a3w, h: 0.44, fontFace: "Microsoft YaHei", fontSize: 14, color: C.A, bold: true, align: "center", valign: "middle" });

  var sections = [
    { title: "① 背景 Background", desc: "问题描述\n发生频次与影响", h: 0.64, c: C.P },
    { title: "② 现状 Current Condition", desc: "数据收集\n流程分析\n问题定位", h: 0.64, c: C.G },
    { title: "③ 目标 Goal", desc: "量化的改善目标\n完成日期", h: 0.64, c: C.TE },
    { title: "④ 根因分析 Root Cause", desc: "5 Why 分析\n鱼骨图\n根本原因", h: 0.64, c: C.D },
    { title: "⑤ 对策 Countermeasures", desc: "消除根因的\n具体对策方案", h: 0.64, c: C.W },
    { title: "⑥ 实施计划 Implementation", desc: "谁来做\n何时做\n在哪做", h: 0.64, c: C.P },
    { title: "⑦ 跟进 Follow-up", desc: "效果验证\n过程监控\n偏差修正", h: 0.64, c: C.G },
    { title: "⑧ 结果 Results", desc: "最终效果\n标准化\n横向展开", h: 0.64, c: C.TE },
  ];

  var col1w = 5.5, col2w = 6.13;
  for (var i = 0; i < sections.length; i++) {
    var sec = sections[i];
    var col = i < 4 ? 0 : 1;
    var row = i < 4 ? i : i - 4;
    var sx = col === 0 ? a3x : a3x + col1w + 0.13;
    var sy = a3y + 0.48 + row * 0.66;
    var sw = col === 0 ? col1w : col2w;
    var bg = row % 2 === 0 ? C.A : C.L;

    s.addShape(S.rect, { x: sx, y: sy, w: sw, h: sec.h, fill: { color: bg }, line: { color: "CBD5E1" } });
    s.addShape(S.rect, { x: sx, y: sy, w: 0.08, h: sec.h, fill: { color: sec.c }, line: { color: "000000" } });
    s.addText(sec.title, { x: sx + 0.16, y: sy + 0.05, w: sw - 0.24, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 10, color: sec.c, bold: true, valign: "middle" });
    s.addText(sec.desc, { x: sx + 0.16, y: sy + 0.3, w: sw - 0.24, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 8.5, color: C.TL, valign: "middle" });
  }

  s.addShape(S.rect, { x: 0.8, y: 6.8, w: 11.73, h: 0.06, fill: { color: C.G }, line: { color: "000000" } });
  s.addText("A3 思维核心：在一张 A3 纸上系统性地呈现问题解决全过程 | Left side: Defined | Right side: Data-driven", { x: 0.8, y: 6.9, w: 11.73, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 10, color: C.TL, align: "center", valign: "middle" });
})();

// ===== SLIDE 04: PDCA =====
(function(){
  var s = pptx.addSlide();
  setBg(s); addTopBar(s, C.G); addTitleBand(s, "PDCA 循环", "Plan-Do-Check-Act Continuous Improvement Cycle"); addFooter(s, "09 | 问题解决方法 | PDCA 循环");
  sectLabel(s, "PART 3 · PDCA");

  var bx = 2.87, by = 1.95, bw = 3.6, bh = 1.7;
  var phases = [
    { x: bx + 4.0, y: by, label: "PLAN\n计划", sub: "分析现状\n设定目标\n制定对策", c: C.P },
    { x: bx + 4.0, y: by + 2.1, label: "DO\n执行", sub: "小范围试行\n收集数据\n记录异常", c: C.G },
    { x: bx, y: by + 2.1, label: "CHECK\n检查", sub: "对比目标\n分析偏差\n确认效果", c: C.W },
    { x: bx, y: by, label: "ACT\n处置", sub: "标准化\n巩固成果\n下一循环", c: C.TE },
  ];
  for (var i = 0; i < phases.length; i++) {
    var p = phases[i];
    s.addShape(S.roundRect, { x: p.x, y: p.y, w: bw, h: bh, fill: { color: p.c }, rectRadius: 0.15, line: { color: p.c } });
    s.addText(p.label, { x: p.x, y: p.y + 0.25, w: bw, h: 0.6, fontFace: "Microsoft YaHei", fontSize: 20, color: C.A, bold: true, align: "center", valign: "middle" });
    s.addText(p.sub, { x: p.x, y: p.y + 0.85, w: bw, h: 0.8, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.A, align: "center", valign: "middle" });
  }

  // Arrows
  // PLAN -> DO (down arrow)
  s.addShape(S.rect, { x: bx + 5.73, y: by + bh + 0.02, w: 0.54, h: 0.28, fill: { color: C.TL }, line: { color: C.TL } });
  // DO -> CHECK (left arrow)
  s.addText("<", { x: bx + 3.55, y: by + 2.75, w: 0.65, h: 0.5, fontFace: "Arial", fontSize: 22, color: C.TL, align: "center", valign: "middle" });
  // CHECK -> ACT (up arrow)
  s.addShape(S.rect, { x: bx + 1.73, y: by + bh + 0.02, w: 0.54, h: 0.28, fill: { color: C.TL }, line: { color: C.TL } });
  s.addText("v", { x: bx + 1.73, y: by + bh - 0.1, w: 0.54, h: 0.28, fontFace: "Arial", fontSize: 14, color: C.TL, align: "center", valign: "middle" });
  // ACT -> PLAN (right arrow)
  s.addText(">", { x: bx + 3.55, y: by + 0.65, w: 0.65, h: 0.5, fontFace: "Arial", fontSize: 22, color: C.TL, align: "center", valign: "middle" });

  // Center spiral
  s.addShape(S.ellipse, { x: bx + 4.93, y: by + 1.3, w: 2.2, h: 1.5, fill: { color: "EEF2FF" }, line: { color: C.P } });
  s.addText("持续改善\nKaizen\n螺旋上升", { x: bx + 4.93, y: by + 1.3, w: 2.2, h: 1.5, fontFace: "Microsoft YaHei", fontSize: 11, color: C.P, bold: true, align: "center", valign: "middle" });

  // Fastener example
  s.addShape(S.rect, { x: 0.5, y: 5.25, w: 12.33, h: 0.06, fill: { color: C.G }, line: { color: "000000" } });
  s.addText("连接件实例：减少螺栓螺纹缺陷率（从 3.2% 降至 <0.5%）", { x: 0.5, y: 5.35, w: 12.33, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 11, color: C.P, bold: true, align: "center" });
  var exSteps = [
    { t: "PLAN: 数据分析，设定 0.5% 缺陷目标", c: C.P, w: 2.95 },
    { t: "DO: 调整攻牙速度/更换丝锥材质试跑", c: C.G, w: 2.95 },
    { t: "CHECK: 统计 3 批缺陷率对比效果", c: C.W, w: 2.95 },
    { t: "ACT: 更新标准作业，培训推广", c: C.TE, w: 2.95 },
  ];
  var ex = 0.5;
  for (var j = 0; j < exSteps.length; j++) {
    var e = exSteps[j];
    s.addShape(S.roundRect, { x: ex, y: 5.8, w: e.w, h: 0.38, fill: { color: e.c }, rectRadius: 0.08, line: { color: e.c } });
    s.addText(e.t, { x: ex, y: 5.8, w: e.w, h: 0.38, fontFace: "Microsoft YaHei", fontSize: 9, color: C.A, align: "center", valign: "middle", bold: true });
    ex += e.w + 0.07;
  }
  s.addText("迭代概念：每一轮 PDCA 推动指标持续改善，从 3.2% 到 1.5% 再到 0.5%", { x: 0.5, y: 6.35, w: 12.33, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 10, color: C.TL, align: "center" });
})();

// ===== SLIDE 05: DMAIC =====
(function(){
  var s = pptx.addSlide();
  setBg(s); addTopBar(s, C.W); addTitleBand(s, "DMAIC 方法论", "Define-Measure-Analyze-Improve-Control"); addFooter(s, "09 | 问题解决方法 | DMAIC 方法论");
  sectLabel(s, "PART 4 · DMAIC");

  // 5 phase flow boxes
  var phases2 = [
    { t: "D 定义", st: "Define", d: "确定项目范围\n定义 CTQ 指标\n组建项目团队", c: C.P },
    { t: "M 测量", st: "Measure", d: "建立数据收集计划\n测量系统分析\n基线数据", c: C.G },
    { t: "A 分析", st: "Analyze", d: "统计分析\n假设检验\n识别关键因子", c: C.W },
    { t: "I 改善", st: "Improve", d: "DOE 实验验证\n方案优选\n实施改善", c: C.TE },
    { t: "C 控制", st: "Control", d: "控制计划\nSPC 控制图\n标准化", c: C.D },
  ];
  var pw = 2.1, ph = 1.35, px0 = 0.55, gap = 0.1;
  for (var i = 0; i < phases2.length; i++) {
    var ph2 = phases2[i];
    var x = px0 + i * (pw + gap);
    s.addShape(S.roundRect, { x: x, y: 1.85, w: pw, h: ph, fill: { color: ph2.c }, rectRadius: 0.1, line: { color: ph2.c } });
    s.addText(ph2.t, { x: x, y: 1.9, w: pw, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 12, color: C.A, bold: true, align: "center", valign: "middle" });
    s.addText(ph2.st, { x: x, y: 2.2, w: pw, h: 0.2, fontFace: "Arial", fontSize: 8, color: C.A, align: "center", valign: "middle" });
    s.addText(ph2.d, { x: x + 0.1, y: 2.45, w: pw - 0.2, h: 0.65, fontFace: "Microsoft YaHei", fontSize: 8, color: C.A, align: "center", valign: "middle" });
    if (i < phases2.length - 1) {
      s.addShape(S.rightArrow, { x: x + pw + 0.02, y: 2.38, w: gap - 0.04, h: 0.3, fill: { color: C.TL }, line: { color: C.TL } });
    }
  }

  // DMAIC vs PDCA comparison
  s.addShape(S.rect, { x: 0.55, y: 3.4, w: 12.23, h: 0.44, fill: { color: C.P }, line: { color: C.P } });
  s.addText("DMAIC vs PDCA  对比分析", { x: 0.55, y: 3.4, w: 12.23, h: 0.44, fontFace: "Microsoft YaHei", fontSize: 13, color: C.A, bold: true, align: "center", valign: "middle" });

  var tx = 0.55, tw = [3.5, 4.0, 4.33];
  s.addShape(S.rect, { x: tx, y: 3.84, w: tw[0] + tw[1] + tw[2], h: 0.38, fill: { color: C.S }, line: { color: C.S } });
  s.addText("对比维度", { x: tx, y: 3.84, w: tw[0], h: 0.38, fontFace: "Microsoft YaHei", fontSize: 10, color: C.P, bold: true, align: "center", valign: "middle" });
  s.addText("PDCA", { x: tx + tw[0], y: 3.84, w: tw[1], h: 0.38, fontFace: "Microsoft YaHei", fontSize: 10, color: C.P, bold: true, align: "center", valign: "middle" });
  s.addText("DMAIC", { x: tx + tw[0] + tw[1], y: 3.84, w: tw[2], h: 0.38, fontFace: "Microsoft YaHei", fontSize: 10, color: C.P, bold: true, align: "center", valign: "middle" });

  var compRows = [
    ["适用场景", "简单/日常问题", "复杂/数据密集"],
    ["数据依赖", "低（经验+观察）", "高（统计分析）"],
    ["工具复杂度", "基础 QC 7 工具", "高级统计 DOE/SPC"],
    ["项目周期", "数天至数周", "数周至数月"],
    ["人员要求", "全员参与", "黑带/绿带认证"],
  ];
  for (var r = 0; r < compRows.length; r++) {
    var ry = 4.22 + r * 0.38;
    var bg = r % 2 === 0 ? C.A : C.L;
    s.addShape(S.rect, { x: tx, y: ry, w: tw[0] + tw[1] + tw[2], h: 0.36, fill: { color: bg }, line: { color: "CBD5E1" } });
    s.addText(compRows[r][0], { x: tx, y: ry, w: tw[0], h: 0.36, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.T, align: "center", valign: "middle" });
    s.addText(compRows[r][1], { x: tx + tw[0], y: ry, w: tw[1], h: 0.36, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.G, align: "center", valign: "middle" });
    s.addText(compRows[r][2], { x: tx + tw[0] + tw[1], y: ry, w: tw[2], h: 0.36, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.W, align: "center", valign: "middle" });
  }

  // When to use
  s.addText("何时使用 DMAIC？  数据量大 + 根因不明确 + 需要严谨验证    何时使用 A3？  问题简单 + 团队共识 + 快速对策", { x: 0.55, y: 6.25, w: 12.23, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 10, color: C.P, bold: true, align: "center" });

  // Fastener example
  s.addShape(S.roundRect, { x: 0.55, y: 6.65, w: 12.23, h: 0.42, fill: { color: "FEF3C7" }, rectRadius: 0.08, line: { color: C.W } });
  s.addText("冷镦机 OEE 提升：D(OEE<60%) -> M(数据采集30天) -> A(停机分析找TOP5) -> I(快速换模+预防保养) -> C(SPC监控稳定>85%)", { x: 0.55, y: 6.65, w: 12.23, h: 0.42, fontFace: "Microsoft YaHei", fontSize: 10, color: C.T, bold: true, align: "center", valign: "middle" });
})();

// ===== SLIDE 06: VA/VE =====
(function(){
  var s = pptx.addSlide();
  setBg(s); addTopBar(s, C.TE); addTitleBand(s, "VA/VE 价值分析/价值工程", "Value Analysis & Value Engineering"); addFooter(s, "09 | 问题解决方法 | VA/VE");
  sectLabel(s, "PART 5 · 价值分析");

  cardB(s, 0.5, 1.78, 5.8, 1.55, C.TE, [
    { t: "VA/VE 核心概念", y: 0.08, size: 13, bold: true, color: C.P },
    { t: "Value = Function / Cost", y: 0.42, size: 11, bold: true, color: C.W },
    { t: "VA: 量产产品的价值提升\nVE: 设计阶段的成本优化", y: 0.7, size: 10, color: C.TL },
    { t: "目标：以最低成本实现必要功能", y: 1.1, size: 10, color: C.T },
  ]);

  // 5-step VA/VE process
  var vsteps = [
    { t: "1\n信息收集", st: "功能规格\n成本数据\n客户需求", c: C.P },
    { t: "2\n功能分析", st: "基本功能\n辅助功能\n功能评价", c: C.G },
    { t: "3\n创意构想", st: "头脑风暴\n替代方案\n材料替换", c: C.W },
    { t: "4\n方案评估", st: "成本对比\n可行性\n风险评估", c: C.TE },
    { t: "5\n实施验证", st: "试做验证\n效果确认\n标准化", c: C.P },
  ];
  var vw = 2.1, vh = 1.05, vx0 = 0.5;
  for (var i = 0; i < vsteps.length; i++) {
    var vs = vsteps[i];
    var x = vx0 + i * (vw + 0.18);
    s.addShape(S.roundRect, { x: x, y: 3.55, w: vw, h: vh, fill: { color: vs.c }, rectRadius: 0.1, line: { color: vs.c } });
    s.addText(vs.t, { x: x, y: 3.6, w: vw, h: 0.4, fontFace: "Microsoft YaHei", fontSize: 10.5, color: C.A, bold: true, align: "center", valign: "middle" });
    s.addText(vs.st, { x: x + 0.05, y: 3.95, w: vw - 0.1, h: 0.55, fontFace: "Microsoft YaHei", fontSize: 8.5, color: C.A, align: "center", valign: "middle" });
    if (i < vsteps.length - 1) {
      s.addShape(S.rightArrow, { x: x + vw + 0.04, y: 3.93, w: 0.1, h: 0.28, fill: { color: C.TL }, line: { color: C.TL } });
    }
  }

  // Cost-value ratio visualization
  s.addShape(S.rect, { x: 0.5, y: 4.8, w: 12.33, h: 0.44, fill: { color: C.P }, line: { color: C.P } });
  s.addText("成本-价值比分析矩阵", { x: 0.5, y: 4.8, w: 12.33, h: 0.44, fontFace: "Microsoft YaHei", fontSize: 13, color: C.A, bold: true, align: "center", valign: "middle" });

  // 2x2 matrix
  var mx = 0.8, my = 5.3, mw = 5.5, mh = 1.35;
  var cells = [
    { x: mx, y: my, lb: "高成本低价值\n重点改善对象", bg: "FEE2C7", tc: C.D },
    { x: mx + mw + 0.3, y: my, lb: "高成本低价值\n功能再设计", bg: "FEE2E2", tc: C.D },
    { x: mx, y: my + mh + 0.25, lb: "低成本高价值\n保持优势", bg: "ECFDF5", tc: C.G },
    { x: mx + mw + 0.3, y: my + mh + 0.25, lb: "高成本高价值\n维持投入", bg: "FEF3C7", tc: C.W },
  ];
  for (var c = 0; c < cells.length; c++) {
    var cl = cells[c];
    s.addShape(S.rect, { x: cl.x, y: cl.y, w: mw, h: mh, fill: { color: cl.bg }, line: { color: "CBD5E1" } });
    s.addText(cl.lb, { x: cl.x, y: cl.y + 0.25, w: mw, h: mh - 0.3, fontFace: "Microsoft YaHei", fontSize: 10, color: cl.tc, align: "center", valign: "middle", bold: true });
  }
  s.addText("低成本高价值", { x: mx + mw + 0.05, y: my + mh * 0.5 - 0.15, w: 0.25, h: 0.3, fontFace: "Arial", fontSize: 8, color: C.TL, align: "center", valign: "middle" });

  // Right side: fastener example
  cardB(s, 7.2, 5.05, 5.63, 2.05, C.TE, [
    { t: "螺栓材料替代 VA/VE 实例", y: 0.08, size: 12, bold: true, color: C.P },
    { t: "Q: 304不锈钢螺栓能否替换？", y: 0.4, size: 10, bold: true, color: C.W },
    { t: "分析：功能需求：防锈+强度 400MPa", y: 0.63, size: 9.5, color: C.T },
    { t: "方案：冷拉碳钢+达克罗涂层", y: 0.86, size: 9.5, color: C.T },
    { t: "效果：材料成本降低 35%（304: 18元/kg vs 碳钢: 6元/kg）", y: 1.09, size: 9.5, color: C.T },
    { t: "验证：盐雾试验 >500h，抗拉 >500MPa OK", y: 1.32, size: 9.5, color: C.G },
    { t: "Cost down 35% | Function equally met", y: 1.72, size: 9.5, bold: true, color: C.G },
  ]);

  // Axis labels
  s.addText("成本", { x: mx - 0.3, y: my + mh, w: 0.6, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 9, color: C.TL, align: "center" });
  s.addText("功\n能", { x: mx + mw * 0.5 - 0.2, y: my + mh * 2 + 0.3, w: 0.4, h: 0.5, fontFace: "Microsoft YaHei", fontSize: 9, color: C.TL, align: "center" });
})();

// ===== SLIDE 07: Method Selection Guide =====
(function(){
  var s = pptx.addSlide();
  setBg(s); addTopBar(s, C.P); addTitleBand(s, "方法选择指南", "Which Method to Use When?"); addFooter(s, "09 | 问题解决方法 | 方法选择指南");
  sectLabel(s, "决策矩阵 · 对症下药");

  // Decision matrix
  var cols = ["A3 报告", "DMAIC", "PDCA", "VA/VE", "Gemba Walk"];
  var colColors = [C.P, C.W, C.G, C.TE, C.D];
  var rowH = 0.36, rh0 = 1.85;
  var cw0 = 2.0, cw = 2.26;
  var rx0 = 1.07;

  // Header row
  s.addShape(S.rect, { x: 0.5, y: rh0, w: cw0, h: 0.44, fill: { color: C.P }, line: { color: C.P } });
  s.addText("场景/维度", { x: 0.5, y: rh0, w: cw0, h: 0.44, fontFace: "Microsoft YaHei", fontSize: 10, color: C.A, bold: true, align: "center", valign: "middle" });
  for (var c = 0; c < cols.length; c++) {
    var cx = rx0 + c * cw;
    s.addShape(S.rect, { x: cx, y: rh0, w: cw, h: 0.44, fill: { color: colColors[c] }, line: { color: colColors[c] } });
    s.addText(cols[c], { x: cx, y: rh0, w: cw, h: 0.44, fontFace: "Microsoft YaHei", fontSize: 10, color: C.A, bold: true, align: "center", valign: "middle" });
  }

  var scenarios = [
    ["问题复杂度", "简单/中等", "复杂/多变量", "中等迭代", "中等/成本", "日常/现场"],
    ["数据需求", "低", "高", "低-中", "中", "无"],
    ["解决周期", "1-2 周", "1-3 月", "2-4 周", "2-4 周", "持续"],
    ["团队规模", "1-3 人", "3-6 人", "2-5 人", "3-5 人", "1-2 人"],
    ["典型场景", "攻牙缺陷率上升", "冷镦机 OEE 降低", "包装效率改善", "螺栓材料降本", "日常巡检改善"],
  ];
  var sceneColors = [C.T, C.TL, C.T, C.T, C.P];

  for (var r = 0; r < scenarios.length; r++) {
    var ry = rh0 + 0.44 + r * rowH;
    var bg = r % 2 === 0 ? C.A : C.L;
    s.addShape(S.rect, { x: 0.5, y: ry, w: cw0, h: rowH, fill: { color: bg }, line: { color: "CBD5E1" } });
    s.addText(scenarios[r][0], { x: 0.5, y: ry, w: cw0, h: rowH, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.P, bold: true, align: "center", valign: "middle" });
    for (var c2 = 0; c2 < cols.length; c2++) {
      var cx = rx0 + c2 * cw;
      s.addShape(S.rect, { x: cx, y: ry, w: cw, h: rowH, fill: { color: bg }, line: { color: "CBD5E1" } });
      s.addText(scenarios[r][c2 + 1], { x: cx, y: ry, w: cw, h: rowH, fontFace: "Microsoft YaHei", fontSize: 9, color: sceneColors[r], align: "center", valign: "middle" });
    }
  }

  // Decision diamond flow
  s.addShape(S.diamond, { x: 0.5, y: 4.3, w: 2.5, h: 1.2, fill: { color: "EEF2FF" }, line: { color: C.P } });
  s.addText("问题发生\nGo to Gemba!", { x: 0.5, y: 4.3, w: 2.5, h: 1.2, fontFace: "Microsoft YaHei", fontSize: 10, color: C.P, bold: true, align: "center", valign: "middle" });

  // Decision flow arrows and boxes
  var dbx = 3.2;
  var decs = [
    { t: "简单问题？\n-> A3", c: C.P, x: dbx },
    { t: "数据密集？\n-> DMAIC", c: C.W, x: dbx + 2.6 },
    { t: "持续改善？\n-> PDCA", c: C.G, x: dbx + 5.2 },
    { t: "成本降低？\n-> VA/VE", c: C.TE, x: dbx + 7.8 },
  ];
  for (var d = 0; d < decs.length; d++) {
    var dk = decs[d];
    s.addShape(S.roundRect, { x: dk.x, y: 4.4, w: 2.3, h: 1.0, fill: { color: dk.c }, rectRadius: 0.1, line: { color: dk.c } });
    s.addText(dk.t, { x: dk.x, y: 4.4, w: 2.3, h: 1.0, fontFace: "Microsoft YaHei", fontSize: 10, color: C.A, bold: true, align: "center", valign: "middle" });
  }

  s.addText("日常 -> Gemba Walk 持续观察 | 方法不是排斥的，可以组合使用", { x: 0.5, y: 5.7, w: 12.33, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 10, color: C.TL, align: "center", bold: true });
  s.addText("组合推荐：Gemba(发现) -> A3(整理) -> PDCA(执行) + DMAIC(分析)", { x: 0.5, y: 6.05, w: 12.33, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 10, color: C.P, bold: true, align: "center" });
})();

// ===== SLIDE 08: Comprehensive Case Study =====
(function(){
  var s = pptx.addSlide();
  setBg(s); addTopBar(s, C.D); addTitleBand(s, "综合案例：多方法组合实战", "End-to-End Problem Solving in Fastener Manufacturing"); addFooter(s, "09 | 问题解决方法 | 综合案例");
  sectLabel(s, "组合应用 · 端到端实战");

  // Case background
  cardB(s, 0.5, 1.78, 12.33, 0.9, C.D, [
    { t: "案例背景：M12 高强螺栓的螺纹缺陷率从 1.2% 突增至 5.8%，客户投诉 3 起", y: 0.08, size: 12, bold: true, color: C.A },
    { t: "挑战：根因不明 | 紧急恢复产能 | 防止复发 | 涉及冷镦-攻牙-热处理三道工序", y: 0.45, size: 10, color: C.A },
  ]);

  // Method flow
  var methods = [
    { t: "STEP 1\nGemba Walk\n现场走动", st: "发现问题", d: "冷镦车间首件检查\n发现螺纹烂牙频次增加\n操作员反馈丝锥磨损快", c: C.G, x: 0.5 },
    { t: "STEP 2\nA3 报告\n结构整理", st: "定义问题", d: "缺陷率趋势图\n划定攻牙工序为瓶颈\n设定目标: <1.5%", c: C.P, x: 3.0 },
    { t: "STEP 3\nPDCA循环\n小步迭代", st: "快速试跑", d: "调整攻牙速度/频率\n统计改善后数据\n验证丝锥更换周期", c: C.W, x: 5.5 },
    { t: "STEP 4\nDMAIC分析\n数据深挖", st: "根因确认", d: "DOE 三因子实验\n确认温度为主因\n优化切削参数组合", c: C.D, x: 8.0 },
    { t: "STEP 5\nResults\n成果验证", st: "标准化", d: "缺陷率降至 0.8%\n更新作业标准\n横向展开至全品类", c: C.TE, x: 10.5 },
  ];
  var mw = 2.15, mh = 1.65, my2 = 2.95;
  for (var i = 0; i < methods.length; i++) {
    var m = methods[i];
    s.addShape(S.roundRect, { x: m.x, y: my2, w: mw, h: mh, fill: { color: m.c }, rectRadius: 0.1, line: { color: m.c } });
    s.addText(m.t, { x: m.x, y: my2 + 0.08, w: mw, h: 0.6, fontFace: "Microsoft YaHei", fontSize: 8, color: C.A, bold: true, align: "center", valign: "middle" });
    s.addText(m.st, { x: m.x, y: my2 + 0.65, w: mw, h: 0.2, fontFace: "Arial", fontSize: 7.5, color: C.A, align: "center", valign: "middle" });
    s.addText(m.d, { x: m.x + 0.08, y: my2 + 0.85, w: mw - 0.16, h: 0.75, fontFace: "Microsoft YaHei", fontSize: 7.5, color: C.A, align: "center", valign: "middle" });
    if (i < methods.length - 1) {
      s.addShape(S.rightArrow, { x: m.x + mw + 0.02, y: my2 + 0.68, w: 0.33, h: 0.28, fill: { color: C.TL }, line: { color: C.TL } });
    }
  }

  // Results summary
  s.addShape(S.rect, { x: 0.5, y: 4.8, w: 12.33, h: 0.44, fill: { color: C.P }, line: { color: C.P } });
  s.addText("改善成果", { x: 0.5, y: 4.8, w: 12.33, h: 0.44, fontFace: "Microsoft YaHei", fontSize: 13, color: C.A, bold: true, align: "center", valign: "middle" });

  statCard(s, 0.5, 5.35, "5.8%", " -> 0.8%", "缺陷率", C.G);
  statCard(s, 3.6, 5.35, "3", "起 -> 0起", "客户投诉", C.TE);
  statCard(s, 6.7, 5.35, "5", "种方法", "组合使用", C.P);
  statCard(s, 9.8, 5.35, "85", "%+", "标准化覆盖", C.W);

  // Key learnings
  var ls = ["Gemba 让管理者亲眼看到现场问题", "A3 帮助团队系统化思考和沟通", "PDCA 小步快跑快速验证", "DMAIC 数据驱动精确根因", "多方法组合威力远大于单一方法"];
  for (var k = 0; k < ls.length; k++) {
    var lx = 0.5 + k * 2.6;
    s.addShape(S.roundRect, { x: lx, y: 6.65, w: 2.45, h: 0.38, fill: { color: k % 2 === 0 ? C.G : C.P }, rectRadius: 0.08, line: { color: k % 2 === 0 ? C.G : C.P } });
    s.addText(ls[k], { x: lx, y: 6.65, w: 2.45, h: 0.38, fontFace: "Microsoft YaHei", fontSize: 8, color: C.A, align: "center", valign: "middle" });
  }
})();

// ===== WRITE FILE =====
pptx.writeFile({ fileName: path.join(OUT, "09-问题解决方法.pptx") })
  .then(function() { console.log("OK: 09-问题解决方法.pptx created"); })
  .catch(function(err) { console.error("ERR:", err); process.exit(1); });
