const PptxGenJS = require("pptxgenjs");
const path = require("path");
const OUT = __dirname;

let pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.title = "5S 管理与看板详解";
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

function addTopBar(slide, color, barH) {
  barH = barH || 0.08;
  slide.addShape(S.rect, { x: 0, y: 0, w: W, h: barH, fill: { color: color }, line: { color: color } });
}
function addTitleBand(slide, title, subtitle) {
  slide.addShape(S.rect, { x: 0, y: 0.08, w: W, h: 1.2, fill: { color: C.P }, line: { color: C.P } });
  slide.addText(title, { x: 0.5, y: 0.12, w: W - 1, h: 0.65, fontFace: "Microsoft YaHei", fontSize: 28, bold: true, color: C.A, align: "left", valign: "middle" });
  if (subtitle) slide.addText(subtitle, { x: 0.5, y: 0.72, w: W - 1, h: 0.45, fontFace: "Microsoft YaHei", fontSize: 13, color: C.S, align: "left", valign: "middle" });
}
function setBg(slide) { slide.background = { color: C.L }; }
function addFooter(slide, text) {
  slide.addShape(S.rect, { x: 0, y: H - 0.35, w: W, h: 0.35, fill: { color: C.T }, line: { color: C.T } });
  slide.addText(text || "精益工具知识库 | 5S管理与看板详解", { x: 0.5, y: H - 0.33, w: W - 1, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 9, color: C.TL, align: "left", valign: "middle" });
}

// ===== SLIDE 1: Chapter Cover =====
function createSlide1() {
  var slide = pptx.addSlide();
  setBg(slide);
  slide.addShape(S.rect, { x: 0, y: 0, w: W, h: H, fill: { color: C.P }, line: { color: C.P } });
  slide.addShape(S.ellipse, { x: W - 4.5, y: -1, w: 5, h: 5, fill: { color: C.S  }, line: { color: "FFFFFF" } });
  slide.addShape(S.ellipse, { x: -1, y: H - 3, w: 4, h: 4, fill: { color: C.G  }, line: { color: "FFFFFF" } });
  slide.addText("04", { x: 0.8, y: 1.2, w: 3.5, h: 3.5, fontFace: "Arial", fontSize: 120, bold: true, color: C.S , align: "left", valign: "middle" });
  slide.addText("5S 管理与看板详解", { x: 0.8, y: 4.2, w: 11, h: 1.2, fontFace: "Microsoft YaHei", fontSize: 40, bold: true, color: C.A, align: "left", valign: "middle" });
  slide.addText("5S Management & Kanban System\n制造精益生产实践", { x: 0.8, y: 5.4, w: 11, h: 0.8, fontFace: "Microsoft YaHei", fontSize: 16, color: C.S, align: "left", valign: "middle" });
  slide.addShape(S.rect, { x: 0.8, y: 6.4, w: 3, h: 0.05, fill: { color: C.G } });
  addFooter(slide);
}

// ===== SLIDE 2: 5S Five Steps =====
function createSlide2() {
  var slide = pptx.addSlide();
  setBg(slide);
  addTopBar(slide, C.P, 0.06);
  addTitleBand(slide, "5S 五个步骤详解", "Five Steps of 5S · 制造应用");
  addFooter(slide);

  var sData = [
    { jp: "Seiri",    cn: "整理", en: "Sort",         desc: "区分必要与不必要物品\n清除废料与多余库存\n释放产线空间", color: "DC2626" },
    { jp: "Seiton",   cn: "整顿", en: "Set in Order", desc: "定点定位定容定量\n工具材料就近放置\n减少寻找浪费",     color: "D97706" },
    { jp: "Seiso",    cn: "清扫", en: "Shine",        desc: "清洁设备与作业面\n检查设备异常\n保持最佳状态",     color: "059669" },
    { jp: "Seiketsu", cn: "清洁", en: "Standardize",  desc: "制定标准与规范\n统一标识色彩\n目视化管理",             color: "0D9488" },
    { jp: "Shitsuke", cn: "素养", en: "Sustain",      desc: "培养良好习惯\n持续改进文化\n自主管理",                 color: "1E2761" },
  ];

  var boxW = 2.1, boxH = 4.8, startX = 0.4, gap = 0.12, startY = 1.5;
  sData.forEach(function(s, i) {
    var x = startX + i * (boxW + gap);
    slide.addShape(S.roundRect, { x: x, y: startY, w: boxW, h: boxH, rectRadius: 0.12, fill: { color: C.A }, line: { color: s.color, width: 2 } });
    slide.addShape(S.rect, { x: x, y: startY, w: boxW, h: 0.85, fill: { color: s.color }, line: { color: s.color } });
    slide.addShape(S.rect, { x: x, y: startY + 0.55, w: boxW, h: 0.3, fill: { color: s.color }, line: { color: s.color } });
    slide.addShape(S.ellipse, { x: x + boxW / 2 - 0.25, y: startY + 0.1, w: 0.5, h: 0.5, fill: { color: C.A }, line: { color: C.A } });
    slide.addText(String(i + 1), { x: x + boxW / 2 - 0.25, y: startY + 0.1, w: 0.5, h: 0.5, fontFace: "Arial", fontSize: 16, bold: true, color: s.color, align: "center", valign: "middle" });
    slide.addText(s.jp, { x: x + 0.1, y: startY + 0.62, w: boxW - 0.2, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 9, color: C.A , align: "center" });
    slide.addText(s.cn, { x: x + 0.1, y: startY + 1.0, w: boxW - 0.2, h: 0.5, fontFace: "Microsoft YaHei", fontSize: 24, bold: true, color: C.A, align: "center", valign: "middle" });
    slide.addShape(S.rect, { x: x + 0.4, y: startY + 1.5, w: boxW - 0.8, h: 0.02, fill: { color: C.A  } });
    slide.addText(s.en, { x: x + 0.1, y: startY + 1.62, w: boxW - 0.2, h: 0.35, fontFace: "Arial", fontSize: 11, color: C.A , align: "center", valign: "middle" });
    slide.addShape(S.rect, { x: x + 0.15, y: startY + 2.1, w: boxW - 0.3, h: 2.4, fill: { color: C.L } });
    var lines = s.desc.split("\n");
    lines.forEach(function(line, li) {
      slide.addShape(S.ellipse, { x: x + 0.22, y: startY + 2.25 + li * 0.45, w: 0.1, h: 0.1, fill: { color: s.color } });
      slide.addText(line, { x: x + 0.35, y: startY + 2.18 + li * 0.45, w: boxW - 0.55, h: 0.38, fontFace: "Microsoft YaHei", fontSize: 9, color: C.T, align: "left", valign: "middle" });
    });
    if (i < 4) {
      slide.addShape(S.rightArrow, { x: x + boxW + 0.02, y: startY + boxH / 2 - 0.12, w: gap - 0.04, h: 0.24, fill: { color: C.S }, line: { color: C.S } });
    }
  });

  slide.addShape(S.roundRect, { x: 0.4, y: startY + boxH + 0.1, w: W - 0.8, h: 0.32, rectRadius: 0.06, fill: { color: C.P  }, line: { color: C.S  } });
  slide.addText("制造要点：从原材料仓→机加工车间→精加工工位→热处理→表面处理→包装发货，全面推行5S确保品质与效率", { x: 0.6, y: startY + boxH + 0.1, w: W - 1.2, h: 0.32, fontFace: "Microsoft YaHei", fontSize: 10, color: C.TL, align: "left", valign: "middle" });
}

// ===== SLIDE 3: 5S Implementation Tools =====
function createSlide3() {
  var slide = pptx.addSlide();
  setBg(slide);
  addTopBar(slide, C.G, 0.06);
  addTitleBand(slide, "5S 实施工具与方法", "5S Implementation Tools · 红牌作战 · 定点摄影 · 清扫点检");
  addFooter(slide);

  // Left: Red Tag Strategy
  slide.addShape(S.roundRect, { x: 0.35, y: 1.5, w: 3.9, h: 5.3, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.D, width: 2 } });
  slide.addShape(S.rect, { x: 0.35, y: 1.5, w: 3.9, h: 0.9, fill: { color: C.D }, line: { color: C.D } });
  slide.addShape(S.rect, { x: 0.35, y: 2.1, w: 3.9, h: 0.3, fill: { color: C.D }, line: { color: C.D } });
  slide.addText("红牌作战", { x: 0.35, y: 1.5, w: 3.9, h: 0.6, fontFace: "Microsoft YaHei", fontSize: 16, bold: true, color: C.A, align: "center", valign: "middle" });
  slide.addText("Red Tag Strategy", { x: 0.35, y: 2.0, w: 3.9, h: 0.35, fontFace: "Arial", fontSize: 10, color: C.A , align: "center" });
  var redItems = [
    { num: "1", text: "确定红牌对象区域（仓库、产线、办公区）" },
    { num: "2", text: "制定'要'与'不要'判定标准" },
    { num: "3", text: "红牌标注：品名/数量/原因/日期" },
    { num: "4", text: "限时处理：保留/转移/报废" },
    { num: "5", text: "跟踪确认，拍照记录改善效果" },
  ];
  redItems.forEach(function(item, i) {
    var iy = 2.55 + i * 0.6;
    slide.addShape(S.roundRect, { x: 0.55, y: iy, w: 0.28, h: 0.28, rectRadius: 0.08, fill: { color: C.D }, line: { color: C.D } });
    slide.addText(item.num, { x: 0.55, y: iy, w: 0.28, h: 0.28, fontFace: "Arial", fontSize: 10, bold: true, color: C.A, align: "center", valign: "middle" });
    slide.addText(item.text, { x: 0.92, y: iy, w: 3.1, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 9.5, color: C.T, align: "left", valign: "middle" });
  });

  // Middle: Before/After Comparison
  slide.addShape(S.roundRect, { x: 4.55, y: 1.5, w: 4.1, h: 5.3, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.G, width: 2 } });
  slide.addShape(S.rect, { x: 4.55, y: 1.5, w: 4.1, h: 0.9, fill: { color: C.G }, line: { color: C.G } });
  slide.addShape(S.rect, { x: 4.55, y: 2.1, w: 4.1, h: 0.3, fill: { color: C.G }, line: { color: C.G } });
  slide.addText("定点摄影看板", { x: 4.55, y: 1.5, w: 4.1, h: 0.6, fontFace: "Microsoft YaHei", fontSize: 16, bold: true, color: C.A, align: "center", valign: "middle" });
  slide.addText("Before / After Comparison", { x: 4.55, y: 2.0, w: 4.1, h: 0.35, fontFace: "Arial", fontSize: 10, color: C.A , align: "center" });
  var photoY = 2.55;
  slide.addShape(S.roundRect, { x: 4.75, y: photoY, w: 1.7, h: 1.3, rectRadius: 0.06, fill: { color: "FEE2E2" }, line: { color: C.D } });
  slide.addText("改善前", { x: 4.75, y: photoY, w: 1.7, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 8, bold: true, color: C.D, align: "center" });
  slide.addShape(S.rect, { x: 4.85, y: photoY + 0.38, w: 0.2, h: 0.65, fill: { color: C.D  } });
  slide.addShape(S.rect, { x: 5.12, y: photoY + 0.50, w: 0.18, h: 0.53, fill: { color: C.TL } });
  slide.addShape(S.rect, { x: 5.42, y: photoY + 0.36, w: 0.22, h: 0.67, fill: { color: C.W  } });
  slide.addShape(S.diamond, { x: 6.0, y: photoY + 0.42, w: 0.3, h: 0.3, fill: { color: C.D  }, line: { color: C.D } });
  slide.addShape(S.rightArrow, { x: 6.5, y: photoY + 0.48, w: 0.5, h: 0.22, fill: { color: C.G }, line: { color: C.G } });
  slide.addShape(S.roundRect, { x: 7.15, y: photoY, w: 1.7, h: 1.3, rectRadius: 0.06, fill: { color: "DCFCE7" }, line: { color: C.G } });
  slide.addText("改善后", { x: 7.15, y: photoY, w: 1.7, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 8, bold: true, color: C.G, align: "center" });
  slide.addShape(S.rect, { x: 7.25, y: photoY + 0.38, w: 0.45, h: 0.3, fill: { color: C.P  }, line: { color: C.P, width: 1 } });
  slide.addShape(S.rect, { x: 7.25, y: photoY + 0.75, w: 0.45, h: 0.3, fill: { color: C.P  }, line: { color: C.P, width: 1 } });
  slide.addShape(S.rect, { x: 7.8, y: photoY + 0.38, w: 0.45, h: 0.3, fill: { color: C.P  }, line: { color: C.P, width: 1 } });
  slide.addShape(S.rect, { x: 7.8, y: photoY + 0.75, w: 0.45, h: 0.3, fill: { color: C.P  }, line: { color: C.P, width: 1 } });
  slide.addShape(S.diamond, { x: 8.35, y: photoY + 0.55, w: 0.28, h: 0.28, fill: { color: C.P  }, line: { color: C.P, width: 1 } });
  // Checklist items below photos
  var ckItems = ["工具按标识归位", "模具分类存放", "废料区域标识", "通道畅通无阻"];
  ckItems.forEach(function(ck, ci) {
    var cy = photoY + 1.55 + ci * 0.38;
    slide.addShape(S.roundRect, { x: 4.75, y: cy, w: 0.2, h: 0.2, rectRadius: 0.04, fill: { color: ci < 2 ? C.D : C.G }, line: { color: ci < 2 ? C.D : C.G } });
    slide.addText(ci < 2 ? "✗" : "✓", { x: 4.75, y: cy, w: 0.2, h: 0.2, fontFace: "Arial", fontSize: 8, bold: true, color: C.A, align: "center", valign: "middle" });
    slide.addText(ck, { x: 5.05, y: cy, w: 3.6, h: 0.2, fontFace: "Microsoft YaHei", fontSize: 9, color: ci < 2 ? C.D : C.G, align: "left", valign: "middle" });
  });

  // Right: Shadow Board & Cleaning Checklist
  slide.addShape(S.roundRect, { x: 8.95, y: 1.5, w: 4.0, h: 5.3, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.TE, width: 2 } });
  slide.addShape(S.rect, { x: 8.95, y: 1.5, w: 4.0, h: 0.9, fill: { color: C.TE }, line: { color: C.TE } });
  slide.addShape(S.rect, { x: 8.95, y: 2.1, w: 4.0, h: 0.3, fill: { color: C.TE }, line: { color: C.TE } });
  slide.addText("形迹管理板 & 清扫点检", { x: 8.95, y: 1.5, w: 4.0, h: 0.6, fontFace: "Microsoft YaHei", fontSize: 14, bold: true, color: C.A, align: "center", valign: "middle" });
  slide.addText("Shadow Board & Cleaning Checklist", { x: 8.95, y: 2.0, w: 4.0, h: 0.35, fontFace: "Arial", fontSize: 9, color: C.A , align: "center" });
  // Shadow board visual
  slide.addShape(S.roundRect, { x: 9.15, y: 2.6, w: 2.0, h: 1.8, rectRadius: 0.06, fill: { color: C.L }, line: { color: C.TE, width: 1 } });
  slide.addText("工具形迹板", { x: 9.15, y: 2.6, w: 2.0, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 8, color: C.TL, align: "center" });
  // Tool outlines
  slide.addShape(S.roundRect, { x: 9.3, y: 2.95, w: 1.3, h: 0.15, rectRadius: 0.04, fill: { color: "FFFFFF" }, line: { color: C.D , width: 1.5, dashType: "dash" } });
  slide.addShape(S.rect, { x: 9.5, y: 3.2, w: 0.8, h: 0.12, fill: { color: "FFFFFF" }, line: { color: C.G , width: 1.5, dashType: "dash" } });
  slide.addShape(S.ellipse, { x: 9.4, y: 3.5, w: 0.5, h: 0.5, fill: { color: "FFFFFF" }, line: { color: C.P , width: 1.5, dashType: "dash" } });
  slide.addShape(S.rightArrow, { x: 9.95, y: 3.58, w: 0.5, h: 0.18, fill: { color: "FFFFFF" }, line: { color: C.D , width: 1.5, dashType: "dash" } });
  // 5S Zones
  slide.addText("5S 责任区域划分：", { x: 9.15, y: 4.55, w: 3.6, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.T });
  var zones = [
    { label: "A区 - 机加工车间", color: C.D },
    { label: "B区 - 精加工工位", color: C.W },
    { label: "C区 - 热处理区", color: C.G },
    { label: "D区 - 表面处理", color: C.TE },
    { label: "E区 - 包装发货", color: C.P },
  ];
  zones.forEach(function(z, zi) {
    var zy = 4.85 + zi * 0.32;
    slide.addShape(S.rect, { x: 9.2, y: zy + 0.05, w: 0.12, h: 0.16, fill: { color: z.color } });
    slide.addText(z.label, { x: 9.4, y: zy, w: 3.3, h: 0.26, fontFace: "Microsoft YaHei", fontSize: 8.5, color: C.T, align: "left", valign: "middle" });
  });
}

// ===== SLIDE 4: 5S Audit & Cases =====
function createSlide4() {
  var slide = pptx.addSlide();
  setBg(slide);
  addTopBar(slide, C.TE, 0.06);
  addTitleBand(slide, "5S 审核表与案例", "5S Audit Checklist · Scoring Criteria · Factory Improvement Cases");
  addFooter(slide);

  // Left: Audit scoring table
  slide.addShape(S.roundRect, { x: 0.35, y: 1.5, w: 6.2, h: 5.4, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.TE, width: 2 } });
  slide.addShape(S.rect, { x: 0.35, y: 1.5, w: 6.2, h: 0.75, fill: { color: C.TE }, line: { color: C.TE } });
  slide.addText("5S 审核评分表", { x: 0.35, y: 1.5, w: 6.2, h: 0.75, fontFace: "Microsoft YaHei", fontSize: 14, bold: true, color: C.A, align: "center", valign: "middle" });

  // Table header
  slide.addShape(S.rect, { x: 0.35, y: 2.25, w: 6.2, h: 0.35, fill: { color: C.P } });
  slide.addText("审核项目", { x: 0.45, y: 2.25, w: 2.5, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.A, align: "left", valign: "middle" });
  slide.addText("评分标准 (0-5分)", { x: 3.0, y: 2.25, w: 2.0, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.A, align: "center", valign: "middle" });
  slide.addText("权重", { x: 5.05, y: 2.25, w: 1.25, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.A, align: "center", valign: "middle" });

  var auditRows = [
    { item: "整理 - 废料清除与分类",  score: "无分类=0  标识清晰=5", weight: "20%", bg: C.L },
    { item: "整顿 - 工具定位与标识",  score: "混乱=0  形迹管理=5",  weight: "25%", bg: C.A },
    { item: "清扫 - 设备与地面清洁",  score: "脏污=0  光亮如新=5",  weight: "20%", bg: C.L },
    { item: "清洁 - 标准化与维持",   score: "无标准=0  目视管理=5", weight: "20%", bg: C.A },
    { item: "素养 - 习惯与纪律",     score: "被动=0  自主管理=5",  weight: "15%", bg: C.L },
  ];
  auditRows.forEach(function(row, ri) {
    var ry = 2.6 + ri * 0.55;
    slide.addShape(S.rect, { x: 0.35, y: ry, w: 6.2, h: 0.55, fill: { color: row.bg } });
    slide.addText(row.item, { x: 0.45, y: ry, w: 2.5, h: 0.55, fontFace: "Microsoft YaHei", fontSize: 9, color: C.T, align: "left", valign: "middle" });
    slide.addText(row.score, { x: 3.0, y: ry, w: 2.0, h: 0.55, fontFace: "Arial", fontSize: 8, color: C.TL, align: "center", valign: "middle" });
    slide.addText(row.weight, { x: 5.05, y: ry, w: 1.25, h: 0.55, fontFace: "Arial", fontSize: 10, bold: true, color: C.TE, align: "center", valign: "middle" });
  });

  // Score interpretation
  slide.addShape(S.roundRect, { x: 0.45, y: 5.55, w: 6.0, h: 1.15, rectRadius: 0.06, fill: { color: C.P  }, line: { color: C.S  } });
  slide.addText("评分等级：", { x: 0.55, y: 5.55, w: 5.8, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.T });
  var grades = [
    { label: "优秀: ≥90分", color: C.G },
    { label: "良好: 75-89分", color: C.TE },
    { label: "合格: 60-74分", color: C.W },
    { label: "不合格: <60分", color: C.D },
  ];
  grades.forEach(function(g, gi) {
    slide.addShape(S.rect, { x: 0.55 + gi * 1.5, y: 5.85, w: 0.12, h: 0.14, fill: { color: g.color } });
    slide.addText(g.label, { x: 0.72 + gi * 1.5, y: 5.82, w: 1.3, h: 0.2, fontFace: "Microsoft YaHei", fontSize: 8, color: C.T, align: "left", valign: "middle" });
  });
  // Recommendation
  slide.addText("改善建议：A/B级维持优势，C级制定30天改善计划，D级停产整顿全面整改", { x: 0.55, y: 6.12, w: 5.8, h: 0.5, fontFace: "Microsoft YaHei", fontSize: 8.5, color: C.TL, align: "left", valign: "middle" });

  // Right: Improvement Cases
  slide.addShape(S.roundRect, { x: 6.85, y: 1.5, w: 6.1, h: 5.4, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.P, width: 2 } });
  slide.addShape(S.rect, { x: 6.85, y: 1.5, w: 6.1, h: 0.75, fill: { color: C.P }, line: { color: C.P } });
  slide.addText("制造工厂 5S 改善案例", { x: 6.85, y: 1.5, w: 6.1, h: 0.75, fontFace: "Microsoft YaHei", fontSize: 14, bold: true, color: C.A, align: "center", valign: "middle" });

  var cases = [
    { title: "案例1 - 工具寻找改善", before: "平均寻找工具: 3.5分钟/次", after: "形迹管理后: 15秒/次", pct: "↓ 93%", color: C.D },
    { title: "案例2 - 废料率降低", before: "废料率: 4.2%", after: "整理实施后: 1.8%", pct: "↓ 57%", color: C.G },
    { title: "案例3 - 换模时间缩短", before: "换模时间: 45分钟", after: "整顿优化后: 20分钟", pct: "↓ 56%", color: C.TE },
    { title: "案例4 - 客诉率改善", before: "月客诉: 12件", after: "5S推行后: 2件", pct: "↓ 83%", color: C.P },
  ];
  cases.forEach(function(c, ci) {
    var cy = 2.45 + ci * 1.15;
    slide.addShape(S.roundRect, { x: 7.0, y: cy, w: 5.8, h: 1.05, rectRadius: 0.06, fill: { color: C.L }, line: { color: c.color  } });
    slide.addShape(S.rect, { x: 7.0, y: cy, w: 0.1, h: 1.05, fill: { color: c.color } });
    slide.addText(c.title, { x: 7.15, y: cy + 0.02, w: 5.6, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 9.5, bold: true, color: c.color });
    slide.addText(c.before, { x: 7.15, y: cy + 0.28, w: 3.2, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 8.5, color: C.D, align: "left", valign: "middle" });
    slide.addShape(S.rightArrow, { x: 7.15 + 3.1, y: cy + 0.32, w: 0.5, h: 0.16, fill: { color: C.TL }, line: { color: C.TL } });
    slide.addText(c.after, { x: 7.15 + 3.6, y: cy + 0.28, w: 2.8, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 8.5, color: C.G, align: "left", valign: "middle" });
    slide.addShape(S.roundRect, { x: 10.3, y: cy + 0.55, w: 1.0, h: 0.35, rectRadius: 0.1, fill: { color: c.color  }, line: { color: c.color } });
    slide.addText(c.pct, { x: 10.3, y: cy + 0.55, w: 1.0, h: 0.35, fontFace: "Arial", fontSize: 11, bold: true, color: c.color, align: "center", valign: "middle" });
  });
}

// ===== SLIDE 5: Kanban System Overview =====
function createSlide5() {
  var slide = pptx.addSlide();
  setBg(slide);
  addTopBar(slide, C.P, 0.06);
  addTitleBand(slide, "看板系统概述", "Kanban System Overview · Production Kanban · Withdrawal Kanban · Signal Kanban");
  addFooter(slide);

  // Top: Definition card
  slide.addShape(S.roundRect, { x: 0.35, y: 1.5, w: 5.8, h: 1.5, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.P, width: 2 } });
  slide.addText("什么是看板？", { x: 0.55, y: 1.55, w: 5.4, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 14, bold: true, color: C.P });
  slide.addText("看板（Kanban）是一种基于可视化卡片的生产拉动式管理系统。通过卡片在工序间传递需求信息，实现'只在需要的时候，按需要的量，生产所需的产品'。", { x: 0.55, y: 1.9, w: 5.4, h: 0.55, fontFace: "Microsoft YaHei", fontSize: 10, color: C.T, align: "left", valign: "top" });
  slide.addText("\"The right product, at the right time, in the right quantity\"", { x: 0.55, y: 2.45, w: 5.4, h: 0.4, fontFace: "Arial", fontSize: 9, italic: true, color: C.TL, align: "left" });

  // Three Kanban types
  var kanbanTypes = [
    { name: "生产看板", en: "Production Kanban", desc: "授权某工序生产\n指定数量的产品\n包含品名/数量/工序", color: C.G, icon: "P" },
    { name: "搬运看板", en: "Withdrawal Kanban", desc: "授权从上游工序\n搬运指定数量的\n物料到下游工序", color: C.TE, icon: "W" },
    { name: "信号看板", en: "Signal Kanban", desc: "当库存低于\n触发点时发出\n批量生产信号", color: C.W, icon: "S" },
  ];
  kanbanTypes.forEach(function(kt, ki) {
    var kx = 0.35 + ki * 4.25;
    slide.addShape(S.roundRect, { x: kx, y: 3.2, w: 4.0, h: 3.6, rectRadius: 0.1, fill: { color: C.A }, line: { color: kt.color, width: 2 } });
    slide.addShape(S.rect, { x: kx, y: 3.2, w: 4.0, h: 0.9, rectRadius: 0.1, fill: { color: kt.color }, line: { color: kt.color } });
    slide.addShape(S.rect, { x: kx, y: 3.8, w: 4.0, h: 0.3, fill: { color: kt.color }, line: { color: kt.color } });
    // Icon circle
    slide.addShape(S.ellipse, { x: kx + 1.5, y: 3.25, w: 1.0, h: 1.0, fill: { color: C.A }, line: { color: kt.color, width: 2 } });
    slide.addText(kt.icon, { x: kx + 1.5, y: 3.28, w: 1.0, h: 1.0, fontFace: "Arial", fontSize: 28, bold: true, color: kt.color, align: "center", valign: "middle" });
    slide.addText(kt.name, { x: kx + 0.2, y: 3.25, w: 3.6, h: 0.4, fontFace: "Microsoft YaHei", fontSize: 14, bold: true, color: C.A, align: "center", valign: "middle" });
    slide.addText(kt.en, { x: kx + 0.2, y: 3.62, w: 3.6, h: 0.3, fontFace: "Arial", fontSize: 9, color: C.A , align: "center" });
    // Desc lines
    var dlines = kt.desc.split("\n");
    dlines.forEach(function(dl, di) {
      var dy = 4.3 + di * 0.3;
      slide.addShape(S.ellipse, { x: kx + 0.25, y: dy + 0.06, w: 0.1, h: 0.1, fill: { color: kt.color } });
      slide.addText(dl, { x: kx + 0.42, y: dy - 0.02, w: 3.4, h: 0.26, fontFace: "Microsoft YaHei", fontSize: 9, color: C.T, align: "left", valign: "middle" });
    });
  });

  // Bottom: Kanban Flow Diagram
  slide.addShape(S.roundRect, { x: 0.35, y: 6.9, w: 12.6, h: 0.35, rectRadius: 0.06, fill: { color: C.P  }, line: { color: C.S  } });
  slide.addText("看板循环流程：供应商 → [原料仓] → [机加工工序] → [精加工工序] → [热处理] → [表面处理] → [包装发货] → 客户    ·    信息流（看板）逆流而下，物流顺流而下", { x: 0.55, y: 6.9, w: 12.2, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 9, color: C.TL, align: "left", valign: "middle" });
}

// ===== SLIDE 6: Kanban Calculation =====
function createSlide6() {
  var slide = pptx.addSlide();
  setBg(slide);
  addTopBar(slide, C.G, 0.06);
  addTitleBand(slide, "看板计算方法", "Kanban Quantity Calculation · WIP Limits · Replenishment Triggers · Numerical Examples");
  addFooter(slide);

  // Formula card
  slide.addShape(S.roundRect, { x: 0.35, y: 1.5, w: 6.2, h: 2.4, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.P, width: 2 } });
  slide.addShape(S.rect, { x: 0.35, y: 1.5, w: 6.2, h: 0.7, fill: { color: C.P }, line: { color: C.P } });
  slide.addText("看板数量计算公式", { x: 0.35, y: 1.5, w: 6.2, h: 0.7, fontFace: "Microsoft YaHei", fontSize: 14, bold: true, color: C.A, align: "center", valign: "middle" });
  // Big formula
  slide.addText("看板张数 = (日需求量 × 补充周期时间 × (1 + 安全系数))  ÷  单箱装载量", { x: 0.55, y: 2.3, w: 5.8, h: 0.5, fontFace: "Microsoft YaHei", fontSize: 11, color: C.TE, align: "center", valign: "middle" });
  var formulaParts = [
    { label: "日需求量", desc: "每日客户/下工序需求", color: C.P },
    { label: "补充周期", desc: "从发出看板到物料到达", color: C.G },
    { label: "安全系数", desc: "通常5%-20%缓冲",    color: C.W },
    { label: "单箱装载", desc: "每箱/容器标准数量",  color: C.TE },
  ];
  formulaParts.forEach(function(fp, fi) {
    var fx = 0.55 + fi * 1.5;
    slide.addShape(S.roundRect, { x: fx, y: 2.9, w: 1.35, h: 0.75, rectRadius: 0.06, fill: { color: fp.color  }, line: { color: fp.color } });
    slide.addText(fp.label, { x: fx, y: 2.92, w: 1.35, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: fp.color, align: "center" });
    slide.addText(fp.desc, { x: fx + 0.08, y: 3.22, w: 1.2, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 7.5, color: C.TL, align: "center", valign: "middle" });
  });

  // Numerical examples
  slide.addShape(S.roundRect, { x: 6.85, y: 1.5, w: 6.1, h: 2.4, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.G, width: 2 } });
  slide.addShape(S.rect, { x: 6.85, y: 1.5, w: 6.1, h: 0.7, fill: { color: C.G }, line: { color: C.G } });
  slide.addText("工件生产实例计算", { x: 6.85, y: 1.5, w: 6.1, h: 0.7, fontFace: "Microsoft YaHei", fontSize: 14, bold: true, color: C.A, align: "center", valign: "middle" });
  var calcRows = [
    { p: "产品", v: "某型号 工件" },
    { p: "日需求量", v: "20,000 件/天" },
    { p: "补充周期", v: "机加工→包装: 0.5天" },
    { p: "安全系数", v: "10%" },
    { p: "单箱装载", v: "500 件/箱" },
  ];
  calcRows.forEach(function(cr, ci) {
    var cy = 2.3 + ci * 0.3;
    slide.addText(cr.p, { x: 7.0, y: cy, w: 1.8, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 9, color: C.TL, align: "left", valign: "middle" });
    slide.addText(cr.v, { x: 8.8, y: cy, w: 3.9, h: 0.28, fontFace: "Arial", fontSize: 9, bold: true, color: C.T, align: "left", valign: "middle" });
  });

  // Results section
  // Left: Worked calculation
  slide.addShape(S.roundRect, { x: 0.35, y: 4.1, w: 6.2, h: 2.5, rectRadius: 0.1, fill: { color: C.P  }, line: { color: C.P  } });
  slide.addText("分步计算", { x: 0.55, y: 4.15, w: 5.8, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 12, bold: true, color: C.P });
  slide.addText("Step 1: 需求总量 = 20,000 × 0.5 = 10,000 件", { x: 0.55, y: 4.5, w: 5.8, h: 0.28, fontFace: "Arial", fontSize: 10, color: C.T });
  slide.addText("Step 2: 含安全库存 = 10,000 × 1.10 = 11,000 件", { x: 0.55, y: 4.8, w: 5.8, h: 0.28, fontFace: "Arial", fontSize: 10, color: C.T });
  slide.addText("Step 3: 看板张数 = 11,000 ÷ 500 = 22 张", { x: 0.55, y: 5.1, w: 5.8, h: 0.28, fontFace: "Arial", fontSize: 10, color: C.T });
  slide.addShape(S.roundRect, { x: 0.55, y: 5.5, w: 5.8, h: 0.85, rectRadius: 0.06, fill: { color: C.G  }, line: { color: C.G } });
  slide.addText("★ 需要看板总数: 22 张", { x: 0.7, y: 5.55, w: 2.0, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 11, bold: true, color: C.G, align: "left", valign: "middle" });
  slide.addText("生产看板: 11张  |  搬运看板: 11张", { x: 2.8, y: 5.55, w: 3.3, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 9, color: C.T, align: "left", valign: "middle" });
  slide.addText("WIP上限 = 表看板数 × 单箱装载量 = 11,000 件", { x: 0.7, y: 5.88, w: 5.5, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 9, color: C.TL, align: "left", valign: "middle" });
  // Additional info
  slide.addText("补货触发点: 当库存低于 5,000件 时发出看板信号", { x: 0.7, y: 6.22, w: 5.5, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 9, color: C.W, align: "left", valign: "middle" });

  // Right: Replenishment triggers
  slide.addShape(S.roundRect, { x: 6.85, y: 4.1, w: 6.1, h: 2.5, rectRadius: 0.1, fill: { color: "FFFBEB" }, line: { color: C.W, width: 2 } });
  slide.addText("补货触发条件", { x: 7.05, y: 4.15, w: 5.7, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 12, bold: true, color: C.W });
  var triggers = [
    { level: "红色预警", desc: "库存 < 安全库存(2天需求)\n立即启动紧急补货", color: C.D },
    { level: "黄色预警", desc: "库存 < 补货点(3天需求)\n正常看板补货流程", color: C.W },
    { level: "绿色正常", desc: "库存 > 补货点\n无需补货，维持现状", color: C.G },
  ];
  triggers.forEach(function(tr, ti) {
    var ty = 4.55 + ti * 0.65;
    slide.addShape(S.rect, { x: 7.0, y: ty, w: 0.12, h: 0.5, fill: { color: tr.color } });
    slide.addText(tr.level, { x: 7.2, y: ty, w: 2.0, h: 0.25, fontFace: "Microsoft YaHei", fontSize: 10, bold: true, color: tr.color, align: "left", valign: "middle" });
    slide.addText(tr.desc, { x: 7.2, y: ty + 0.23, w: 5.5, h: 0.38, fontFace: "Microsoft YaHei", fontSize: 8.5, color: C.T, align: "left", valign: "top" });
  });

  // Bottom: WIP Limits
  slide.addShape(S.roundRect, { x: 0.35, y: 6.85, w: 12.6, h: 0.35, rectRadius: 0.06, fill: { color: C.P  }, line: { color: C.S  } });
  slide.addText("精益原则：WIP（在制品）= 看板数 × 单箱装载量。限制WIP是控制生产节拍、缩短交期的核心手段。看板数量 = 生产节拍的控制阀。", { x: 0.55, y: 6.85, w: 12.2, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 9, color: C.TL, align: "left", valign: "middle" });
}

// ===== SLIDE 7: Kanban Implementation Case =====
function createSlide7() {
  var slide = pptx.addSlide();
  setBg(slide);
  addTopBar(slide, C.TE, 0.06);
  addTitleBand(slide, "看板实施案例", "Manufacturing Production Kanban · Machining → Precision Machining → Heat Treatment → Surface Treatment");
  addFooter(slide);

  // Top: Flow diagram of processes
  var processes = [
    { name: "原料仓\nMaterial\nWarehouse",   color: C.P },
    { name: "机加工\nMachining",            color: C.D },
    { name: "精加工\nPrecision\nMachining",           color: C.W },
    { name: "热处理\nHeat\nTreatment",         color: C.G },
    { name: "表面处理\nSurface\nTreatment",    color: C.TE },
    { name: "包装发货\nPack &\nShip",         color: C.P },
  ];
  var procW = 1.7, procH = 1.1, procStartX = 0.35, procGap = 0.22, procY = 1.5;

  processes.forEach(function(p, pi) {
    var px = procStartX + pi * (procW + procGap);
    // Process box
    slide.addShape(S.roundRect, { x: px, y: procY, w: procW, h: procH, rectRadius: 0.1, fill: { color: p.color }, line: { color: p.color } });
    slide.addText(p.name, { x: px, y: procY, w: procW, h: procH, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.A, align: "center", valign: "middle" });
    // Arrow to next
    if (pi < processes.length - 1) {
      slide.addShape(S.rightArrow, { x: px + procW + 0.02, y: procY + procH / 2 - 0.1, w: procGap - 0.04, h: 0.2, fill: { color: C.S }, line: { color: C.S } });
    }
    // Kanban card between processes
    if (pi < processes.length - 1) {
      var cardX = px + procW + 0.04;
      var cardY = procY + procH + 0.15;
      slide.addShape(S.roundRect, { x: cardX, y: cardY, w: procGap - 0.08, h: 0.8, rectRadius: 0.04, fill: { color: C.A }, line: { color: p.color, width: 1.5 } });
      slide.addText("看板#" + (pi + 1), { x: cardX, y: cardY, w: procGap - 0.08, h: 0.22, fontFace: "Arial", fontSize: 7, bold: true, color: p.color, align: "center" });
      slide.addText("品名/数量/时间", { x: cardX + 0.04, y: cardY + 0.22, w: procGap - 0.16, h: 0.22, fontFace: "Microsoft YaHei", fontSize: 6, color: C.TL, align: "center" });
      // Down arrow from card to process
      slide.addShape(S.rect, { x: cardX + (procGap - 0.08) / 2 - 0.02, y: cardY + 0.8, w: 0.04, h: 0.15, fill: { color: C.S } });
    }
  });

  // Middle: Kanban card design examples
  slide.addShape(S.roundRect, { x: 0.35, y: 3.6, w: 6.2, h: 3.2, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.P, width: 2 } });
  slide.addShape(S.rect, { x: 0.35, y: 3.6, w: 6.2, h: 0.65, fill: { color: C.P }, line: { color: C.P } });
  slide.addText("看板卡片设计示例", { x: 0.35, y: 3.6, w: 6.2, h: 0.65, fontFace: "Microsoft YaHei", fontSize: 13, bold: true, color: C.A, align: "center", valign: "middle" });

  // Card 1: Production Kanban
  slide.addShape(S.roundRect, { x: 0.55, y: 4.4, w: 2.8, h: 2.15, rectRadius: 0.06, fill: { color: C.L }, line: { color: C.G, width: 1.5 } });
  slide.addShape(S.rect, { x: 0.55, y: 4.4, w: 2.8, h: 0.35, fill: { color: C.G }, line: { color: C.G } });
  slide.addText("生产看板", { x: 0.55, y: 4.4, w: 2.8, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.A, align: "center", valign: "middle" });
  var card1Fields = ["产品: 某型号工件", "数量: 5,000件", "工序: 机加工→精加工", "交期: 当日14:00", "看板号: P-001"];
  card1Fields.forEach(function(f, fi) {
    slide.addText(f, { x: 0.65, y: 4.85 + fi * 0.28, w: 2.6, h: 0.24, fontFace: "Microsoft YaHei", fontSize: 8, color: C.T, align: "left", valign: "middle" });
  });

  // Card 2: Withdrawal Kanban
  slide.addShape(S.roundRect, { x: 3.55, y: 4.4, w: 2.8, h: 2.15, rectRadius: 0.06, fill: { color: C.L }, line: { color: C.TE, width: 1.5 } });
  slide.addShape(S.rect, { x: 3.55, y: 4.4, w: 2.8, h: 0.35, fill: { color: C.TE }, line: { color: C.TE } });
  slide.addText("搬运看板", { x: 3.55, y: 4.4, w: 2.8, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.A, align: "center", valign: "middle" });
  var card2Fields = ["物料: 机加工半成品", "数量: 500件/箱 × 2箱", "从: 机加工车间", "到: 精加工工位", "看板号: W-003"];
  card2Fields.forEach(function(f, fi) {
    slide.addText(f, { x: 3.65, y: 4.85 + fi * 0.28, w: 2.6, h: 0.24, fontFace: "Microsoft YaHei", fontSize: 8, color: C.T, align: "left", valign: "middle" });
  });

  // Right: Implementation steps
  slide.addShape(S.roundRect, { x: 6.85, y: 3.6, w: 6.1, h: 3.2, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.G, width: 2 } });
  slide.addShape(S.rect, { x: 6.85, y: 3.6, w: 6.1, h: 0.65, fill: { color: C.G }, line: { color: C.G } });
  slide.addText("看板实施步骤", { x: 6.85, y: 3.6, w: 6.1, h: 0.65, fontFace: "Microsoft YaHei", fontSize: 13, bold: true, color: C.A, align: "center", valign: "middle" });
  var steps = [
    { num: "1", text: "分析各工序节拍时间(Takt Time)与换线时间", color: C.P },
    { num: "2", text: "计算各工序间看板数量与安全库存", color: C.G },
    { num: "3", text: "设计看板卡片格式(纸质/电子)", color: C.TE },
    { num: "4", text: "设置看板回收箱与信号灯系统", color: C.W },
    { num: "5", text: "培训员工看板使用规则与流程", color: C.D },
    { num: "6", text: "试运行→收集数据→优化看板数量", color: C.P },
  ];
  steps.forEach(function(s, si) {
    var sy = 4.35 + si * 0.38;
    slide.addShape(S.roundRect, { x: 7.0, y: sy, w: 0.28, h: 0.28, rectRadius: 0.08, fill: { color: s.color }, line: { color: s.color } });
    slide.addText(s.num, { x: 7.0, y: sy, w: 0.28, h: 0.28, fontFace: "Arial", fontSize: 9, bold: true, color: C.A, align: "center", valign: "middle" });
    slide.addText(s.text, { x: 7.38, y: sy, w: 5.35, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 8.5, color: C.T, align: "left", valign: "middle" });
  });

  // Bottom: Results
  slide.addShape(S.roundRect, { x: 0.35, y: 7.0, w: 12.6, h: 0.22, rectRadius: 0.06, fill: { color: C.G  }, line: { color: C.G  } });
  slide.addText("实施效果：某工厂推行看板后，在制品库存降低45%，交期缩短30%，换线时间减少25%，月产能提升15%", { x: 0.55, y: 7.0, w: 12.2, h: 0.22, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.G, align: "left", valign: "middle" });
}

// ===== SLIDE 8: Summary =====
function createSlide8() {
  var slide = pptx.addSlide();
  setBg(slide);
  addTopBar(slide, C.P, 0.08);
  addTitleBand(slide, "总结：5S 与看板的协同效应", "5S & Kanban Synergy · Continuous Improvement · Action Plan");
  addFooter(slide);

  // Left: 5S + Kanban relationship
  slide.addShape(S.roundRect, { x: 0.35, y: 1.5, w: 6.0, h: 3.5, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.P, width: 2 } });
  slide.addShape(S.rect, { x: 0.35, y: 1.5, w: 6.0, h: 0.7, fill: { color: C.P }, line: { color: C.P } });
  slide.addText("5S 与看板的协同关系", { x: 0.35, y: 1.5, w: 6.0, h: 0.7, fontFace: "Microsoft YaHei", fontSize: 14, bold: true, color: C.A, align: "center", valign: "middle" });

  // Two overlapping circles (Venn diagram style)
  slide.addShape(S.ellipse, { x: 1.2, y: 2.5, w: 2.2, h: 2.2, fill: { color: C.P  }, line: { color: C.P, width: 2 } });
  slide.addText("5S管理\n目视化基础\n标准化作业\n清洁有序环境", { x: 1.2, y: 2.9, w: 2.2, h: 1.6, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.P, align: "center", valign: "middle" });

  slide.addShape(S.ellipse, { x: 3.6, y: 2.5, w: 2.2, h: 2.2, fill: { color: C.G  }, line: { color: C.G, width: 2 } });
  slide.addText("看板系统\n拉动式生产\nWIP控制\n节奏化制造", { x: 3.6, y: 2.9, w: 2.2, h: 1.6, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.G, align: "center", valign: "middle" });

  // Overlap region
  slide.addShape(S.ellipse, { x: 2.7, y: 3.1, w: 1.0, h: 1.0, fill: { color: C.TE  }, line: { color: C.TE, width: 1.5 } });
  slide.addText("精益\n生产", { x: 2.7, y: 3.1, w: 1.0, h: 1.0, fontFace: "Microsoft YaHei", fontSize: 10, bold: true, color: C.TE, align: "center", valign: "middle" });

  // Right: Key takeaways
  slide.addShape(S.roundRect, { x: 6.65, y: 1.5, w: 6.3, h: 3.5, rectRadius: 0.1, fill: { color: C.A }, line: { color: C.G, width: 2 } });
  slide.addShape(S.rect, { x: 6.65, y: 1.5, w: 6.3, h: 0.7, fill: { color: C.G }, line: { color: C.G } });
  slide.addText("核心要点回顾", { x: 6.65, y: 1.5, w: 6.3, h: 0.7, fontFace: "Microsoft YaHei", fontSize: 14, bold: true, color: C.A, align: "center", valign: "middle" });

  var keyPoints = [
    { icon: "✓", text: "5S是精益基础：整理→整顿→清扫→清洁→素养，持续循环改善", color: C.P },
    { icon: "✓", text: "红牌作战、定点摄影、形迹管理是5S落地的核心工具", color: C.G },
    { icon: "✓", text: "看板数量 = (日需求×补充周期×(1+安全系数))÷单箱装载量", color: C.TE },
    { icon: "✓", text: "三种看板：生产看板、搬运看板、信号看板各有适用场景", color: C.W },
    { icon: "✓", text: "5S与看板协同：5S创造有序环境，看板驱动拉动式生产", color: C.P },
  ];
  keyPoints.forEach(function(kp, ki) {
    var ky = 2.35 + ki * 0.5;
    slide.addText(kp.icon, { x: 6.85, y: ky, w: 0.35, h: 0.35, fontFace: "Arial", fontSize: 12, bold: true, color: kp.color, align: "left", valign: "middle" });
    slide.addText(kp.text, { x: 7.15, y: ky, w: 5.6, h: 0.35, fontFace: "Microsoft YaHei", fontSize: 8.5, color: C.T, align: "left", valign: "middle" });
  });

  // Bottom: Action Plan
  slide.addShape(S.roundRect, { x: 0.35, y: 5.3, w: 12.6, h: 1.6, rectRadius: 0.1, fill: { color: "EFF6FF" }, line: { color: C.S  } });
  slide.addText("行动计划建议", { x: 0.55, y: 5.35, w: 12.2, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 12, bold: true, color: C.P });

  var planPhases = [
    { phase: "第1-2周", desc: "5S启动",      detail: "组建5S小组，全员培训，红牌作战",                color: C.D },
    { phase: "第3-4周", desc: "5S深化",      detail: "定点定位，形迹管理，审核评分",                   color: C.W },
    { phase: "第5-8周", desc: "看板导入",    detail: "计算看板数量，设计卡片，试运行",                color: C.G },
    { phase: "第9-12周", desc: "持续改善",   desc: "优化看板数量，标准化，成果固化",                color: C.P },
  ];
  var planW = 2.8;
  planPhases.forEach(function(pp, pi) {
    var px = 0.55 + pi * (planW + 0.15);
    slide.addShape(S.roundRect, { x: px, y: 5.7, w: planW, h: 1.0, rectRadius: 0.06, fill: { color: pp.color  }, line: { color: pp.color } });
    slide.addShape(S.rect, { x: px, y: 5.7, w: planW, h: 0.3, fill: { color: pp.color } });
    slide.addText(pp.phase, { x: px, y: 5.7, w: planW, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 9, bold: true, color: C.A, align: "center", valign: "middle" });
    slide.addText(pp.desc, { x: px + 0.1, y: 6.02, w: planW - 0.2, h: 0.28, fontFace: "Microsoft YaHei", fontSize: 10, bold: true, color: pp.color, align: "center" });
    slide.addText(pp.detail, { x: px + 0.1, y: 6.32, w: planW - 0.2, h: 0.3, fontFace: "Microsoft YaHei", fontSize: 7.5, color: C.TL, align: "center", valign: "middle" });
  });
}

// ==================== Generate all slides ====================
createSlide1();
createSlide2();
createSlide3();
createSlide4();
createSlide5();
createSlide6();
createSlide7();
createSlide8();

var OUTFILE = path.join(OUT, "04-5S管理与看板详解.pptx");
pptx.writeFile({ fileName: OUTFILE }).then(function() {
  console.log("SUCCESS: " + OUTFILE);
}).catch(function(err) {
  console.error("ERROR: " + err.message);
  process.exit(1);
});
