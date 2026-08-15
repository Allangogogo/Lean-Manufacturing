const PptxGenJS = require("pptxgenjs");

const pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "精益工具知识库";
pptx.title = "精益工具知识库";

const W = 13.33;
const H = 7.5;

function addTopBar(slide, color, barH) {
  slide.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0, w: W, h: barH || 0.08,
    fill: { color: color }, line: { color: color, width: 0 }
  });
}

function addTitleBand(slide, title, subtitle) {
  slide.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0.08, w: W, h: 0.92,
    fill: { color: "1E2761" }, line: { color: "1E2761", width: 0 }
  });
  slide.addText(title, {
    x: 0.5, y: 0.12, w: W - 1, h: 0.52,
    fontFace: "Arial Black", fontSize: 28, color: "FFFFFF",
    bold: true, valign: "middle"
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.5, y: 0.54, w: W - 1, h: 0.35,
      fontFace: "Arial", fontSize: 14, color: "CADCFC",
      valign: "middle"
    });
  }
}

function setBg(slide) {
  slide.addShape(pptx.ShapeType.rect, {
    x: 0, y: 0.08, w: W, h: H - 0.08,
    fill: { color: "F8FAFC" }, line: { color: "F8FAFC", width: 0 }
  });
}

function addFooter(slide, text) {
  slide.addShape(pptx.ShapeType.rect, {
    x: 0, y: H - 0.32, w: W, h: 0.32,
    fill: { color: "1E2761" }, line: { color: "1E2761", width: 0 }
  });
  slide.addText(text, {
    x: 0, y: H - 0.32, w: W, h: 0.32,
    fontFace: "Arial", fontSize: 11, color: "CADCFC",
    align: "center", valign: "middle"
  });
}

// ============ SLIDE 1: COVER ============
const s1 = pptx.addSlide();
s1.addShape(pptx.ShapeType.rect, {
  x: 0, y: 0, w: W, h: H,
  fill: { color: "1E2761" }, line: { color: "1E2761", width: 0 }
});
addTopBar(s1, "0D9488", 0.12);

s1.addShape(pptx.ShapeType.rect, {
  x: 8.5, y: 0, w: 1.5, h: H,
  fill: { color: "0F172A" }, transparency: 70,
  line: { color: "0F172A", width: 0 }
});

s1.addShape(pptx.ShapeType.ellipse, {
  x: 9.0, y: 1.2, w: 2.8, h: 2.8,
  fill: { color: "0D9488" }, transparency: 82,
  line: { color: "0D9488", width: 0 }
});
s1.addShape(pptx.ShapeType.ellipse, {
  x: 10.2, y: 3.2, w: 2.0, h: 2.0,
  fill: { color: "FFFFFF" }, transparency: 88,
  line: { color: "FFFFFF", width: 0 }
});
s1.addShape(pptx.ShapeType.hexagon, {
  x: 9.3, y: 5.2, w: 2.2, h: 2.2,
  fill: { color: "F59E0B" }, transparency: 78,
  line: { color: "F59E0B", width: 0 }
});

s1.addText("精益工具知识库", {
  x: 0.8, y: 1.2, w: 7.5, h: 1.0,
  fontFace: "Arial Black", fontSize: 44, color: "FFFFFF",
  bold: true, valign: "middle"
});
s1.addText("离散制造企业精益转型核心指南", {
  x: 0.8, y: 2.3, w: 7.5, h: 0.6,
  fontFace: "Arial", fontSize: 20, color: "CADCFC",
  valign: "middle"
});

s1.addShape(pptx.ShapeType.rect, {
  x: 0.8, y: 3.25, w: 3.0, h: 0.05,
  fill: { color: "0D9488" }, line: { color: "0D9488", width: 0 }
});
s1.addShape(pptx.ShapeType.rect, {
  x: 0.8, y: 3.32, w: 1.5, h: 0.05,
  fill: { color: "F59E0B" }, line: { color: "F59E0B", width: 0 }
});

s1.addText("打造适合制造业的精益知识体系", {
  x: 0.8, y: 3.55, w: 6.5, h: 0.5,
  fontFace: "Arial", fontSize: 14, color: "94A3B8",
  valign: "middle"
});

const stats = [
  { num: "13+", label: "核心精益工具" },
  { num: "5",   label: "问题解决方法" },
  { num: "4",   label: "深度专题研究" },
  { num: "70%", label: "转型失败率*" }
];
const cardW = 1.5;
stats.forEach(function(s, i) {
  const cx = 0.5 + i * (cardW + 0.12);
  s1.addShape(pptx.ShapeType.roundRect, {
    x: cx, y: 4.8, w: cardW, h: 1.35,
    fill: { color: "FFFFFF" }, transparency: 10,
    line: { color: "0D9488", width: 0.75 },
    rectRadius: 0.06
  });
  s1.addShape(pptx.ShapeType.rect, {
    x: cx, y: 4.8, w: cardW, h: 0.05,
    fill: { color: i === 3 ? "F59E0B" : "0D9488" },
    line: { color: "0D9488", width: 0 }
  });
  s1.addText(s.num, {
    x: cx, y: 4.9, w: cardW, h: 0.65,
    fontFace: "Arial Black", fontSize: 24, color: "FFFFFF",
    align: "center", bold: true, valign: "middle"
  });
  s1.addText(s.label, {
    x: cx, y: 5.5, w: cardW, h: 0.5,
    fontFace: "Arial", fontSize: 11, color: "CADCFC",
    align: "center", valign: "middle"
  });
});

s1.addText("* 精益转型失败率高达 70%，根本原因在于变革管理而非工具技术", {
  x: 0.5, y: 6.65, w: 10, h: 0.35,
  fontFace: "Arial", fontSize: 10, color: "64748B",
  valign: "middle"
});

// ============ SLIDE 2: CONTENTS ============
const s2 = pptx.addSlide();
setBg(s2);
addTopBar(s2, "0D9488");
addTitleBand(s2, "知识库目录", "Contents");

const tocItems = [
  { title: "01 精益基础",        desc: "精益哲学 . 八大浪费 . TPS体系 . 术语表",              color: "0D9488" },
  { title: "02 核心工具（13+）", desc: "看板 . VSM . 安灯 . 标准作业 . TPM . 5S 等",         color: "1E2761" },
  { title: "03 问题解决方法",    desc: "Gemba Walk . A3 . PDCA . DMAIC . VA/VE",             color: "F59E0B" },
  { title: "04 制造工序应用",  desc: "机加工 . 精加工 . 热处理 . 表面处理 . 包装",             color: "0891B2" },
  { title: "05 实践案例集",      desc: "SMED改善案例 . 改善提案模板 . 实施指南",              color: "7C3AED" },
  { title: "06 深度专题研究",    desc: "变革管理 . VSM高级实战 . 质量标准整合 . 精益数字化",  color: "DC2626" }
];

const tcW = 5.8, tcH = 1.15;
const tcX1 = 0.4, tcX2 = 7.0;
tocItems.forEach(function(item, i) {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const cx = col === 0 ? tcX1 : tcX2;
  const cy = 1.25 + row * 1.55;

  s2.addShape(pptx.ShapeType.rect, {
    x: cx + 0.03, y: cy + 0.03, w: tcW, h: tcH,
    fill: { color: "000000" }, transparency: 88,
    line: { color: "000000", width: 0 }, rectRadius: 0.08
  });
  s2.addShape(pptx.ShapeType.rect, {
    x: cx, y: cy, w: tcW, h: tcH,
    fill: { color: "FFFFFF" },
    line: { color: "E2E8F0", width: 0.5 }, rectRadius: 0.08
  });
  s2.addShape(pptx.ShapeType.rect, {
    x: cx, y: cy, w: 0.12, h: tcH,
    fill: { color: item.color }, line: { color: item.color, width: 0 }
  });
  s2.addShape(pptx.ShapeType.rect, {
    x: cx, y: cy + 0.12, w: 0.12, h: tcH - 0.24,
    fill: { color: item.color }, line: { color: item.color, width: 0 }
  });
  s2.addText(item.title, {
    x: cx + 0.3, y: cy + 0.12, w: tcW - 0.5, h: 0.45,
    fontFace: "Arial Black", fontSize: 16, color: "1E2761",
    bold: true, valign: "middle"
  });
  s2.addText(item.desc, {
    x: cx + 0.3, y: cy + 0.55, w: tcW - 0.6, h: 0.45,
    fontFace: "Arial", fontSize: 11, color: "64748B",
    valign: "middle"
  });
  s2.addShape(pptx.ShapeType.ellipse, {
    x: cx + tcW - 0.38, y: cy + tcH / 2 - 0.1, w: 0.2, h: 0.2,
    fill: { color: item.color }, line: { color: item.color, width: 0 }
  });
});

addFooter(s2, "共 6 大模块 | 13+ 核心工具 | 覆盖制造全流程");

// ============ SLIDE 3: FIVE PRINCIPLES ============
const s3 = pptx.addSlide();
setBg(s3);
addTopBar(s3, "0D9488");
addTitleBand(s3, "精益哲学与原则", "Lean Philosophy & Principles");

const principles = [
  { symbol: "◎", name: "价值 (Value)",         desc: "从客户角度定义价值" },
  { symbol: "⇒", name: "价值流 (Value Stream)", desc: "识别价值创造流程" },
  { symbol: "▶", name: "流动 (Flow)",           desc: "让价值持续流动" },
  { symbol: "◀", name: "拉动 (Pull)",           desc: "按需拉动生产" },
  { symbol: "∞", name: "尽善尽美 (Perfection)", desc: "追求持续改善" }
];

const pDia = 1.2, pGap = 1.25;
const pStartX = 1.0, pY = 1.65;

principles.forEach(function(p, i) {
  const pcx = pStartX + i * (pDia + pGap);

  s3.addShape(pptx.ShapeType.ellipse, {
    x: pcx, y: pY, w: pDia, h: pDia,
    fill: { color: "1E2761" },
    line: { color: "0D9488", width: 2 }
  });

  s3.addText(String(i + 1), {
    x: pcx + pDia / 2 - 0.2, y: pY - 0.32, w: 0.4, h: 0.4,
    fontFace: "Arial Black", fontSize: 12, color: "0D9488",
    align: "center", valign: "middle"
  });

  s3.addText(p.symbol, {
    x: pcx, y: pY, w: pDia, h: pDia,
    fontFace: "Arial", fontSize: 32, color: "0D9488",
    align: "center", valign: "middle"
  });

  if (i < principles.length - 1) {
    const arX = pcx + pDia + 0.05;
    s3.addShape(pptx.ShapeType.rect, {
      x: arX, y: pY + pDia / 2 - 0.02, w: pGap - 0.1, h: 0.04,
      fill: { color: "0D9488" }, line: { color: "0D9488", width: 0 }
    });
    s3.addShape(pptx.ShapeType.rtTriangle, {
      x: arX + pGap - 0.18, y: pY + pDia / 2 - 0.1, w: 0.13, h: 0.2,
      fill: { color: "0D9488" }, line: { color: "0D9488", width: 0 }
    });
  }

  s3.addText(p.name, {
    x: pcx - 0.15, y: pY + pDia + 0.1, w: pDia + 0.3, h: 0.32,
    fontFace: "Arial Black", fontSize: 10, color: "1E2761",
    align: "center", bold: true, valign: "middle"
  });
  s3.addText(p.desc, {
    x: pcx - 0.2, y: pY + pDia + 0.38, w: pDia + 0.4, h: 0.3,
    fontFace: "Arial", fontSize: 8, color: "64748B",
    align: "center", valign: "middle"
  });
});

s3.addShape(pptx.ShapeType.rect, {
  x: 0.5, y: 3.55, w: W - 1.0, h: 0.04,
  fill: { color: "1E2761" }, line: { color: "1E2761", width: 0 }
});

s3.addShape(pptx.ShapeType.roundRect, {
  x: 0.4, y: 3.8, w: W - 0.8, h: 2.2,
  fill: { color: "EBF4FF" },
  line: { color: "BFDBFE", width: 0.5 },
  rectRadius: 0.1
});
s3.addText("精益核心理念", {
  x: 0.7, y: 3.85, w: 3, h: 0.45,
  fontFace: "Arial Black", fontSize: 16, color: "1E2761",
  bold: true, valign: "middle"
});

const coreConcepts = [
  { icon: "M", label: "消除浪费 (Muda)",    color: "DC2626", desc: "识别并消除七大浪费，释放隐藏产能" },
  { icon: "K", label: "持续改善 (Kaizen)",  color: "0D9488", desc: "从小做起，全员参与，持续优化流程" },
  { icon: "R", label: "尊重人格 (Respect)",  color: "F59E0B", desc: "激发员工潜能，培养问题解决的专家" },
  { icon: "G", label: "现地现物 (Genchi)",   color: "1E2761", desc: "深入现场，用事实说话，数据驱动决策" }
];
coreConcepts.forEach(function(c, i) {
  const x = 0.6 + i * 3.2;
  s3.addShape(pptx.ShapeType.ellipse, {
    x: x, y: 4.35, w: 0.5, h: 0.5,
    fill: { color: c.color }, line: { color: c.color, width: 0 }
  });
  s3.addText(c.icon, {
    x: x, y: 4.35, w: 0.5, h: 0.5,
    fontFace: "Arial Black", fontSize: 14, color: "FFFFFF",
    align: "center", bold: true, valign: "middle"
  });
  s3.addText(c.label, {
    x: x + 0.6, y: 4.35, w: 2.4, h: 0.5,
    fontFace: "Arial Black", fontSize: 12, color: c.color,
    bold: true, valign: "middle"
  });
  s3.addText(c.desc, {
    x: x, y: 4.95, w: 3.0, h: 0.7,
    fontFace: "Arial", fontSize: 10, color: "475569",
    valign: "top", wrap: true
  });
});

addFooter(s3, "TPS 两大支柱：准时化 (JIT) 与 自働化 (Jidoka)");

// ============ SLIDE 4: 8 WASTES ============
const s4 = pptx.addSlide();
setBg(s4);
addTopBar(s4, "0D9488");
addTitleBand(s4, "八大浪费识别指南", "8 Wastes (Muda) Identification Guide");

const wastes = [
  { cn: "过量生产",   en: "Overproduction",   pct: 35, color: "DC2626", desc: "生产超出客户需求" },
  { cn: "等待",       en: "Waiting",          pct: 20, color: "EA580C", desc: "人员/设备闲置" },
  { cn: "库存",       en: "Inventory",        pct: 15, color: "CA8A04", desc: "过多原材料/在制品" },
  { cn: "搬运",       en: "Transportation",   pct: 10, color: "F59E0B", desc: "不必要的物料移动" },
  { cn: "过度加工",   en: "Over-processing",  pct: 8,  color: "EAB308", desc: "超出客户要求的加工" },
  { cn: "动作",       en: "Motion",           pct: 5,  color: "0D9488", desc: "不必要的人员动作" },
  { cn: "不良品",     en: "Defects",          pct: 5,  color: "7C3AED", desc: "返工/废品/重复检验" },
  { cn: "未利用人才", en: "Unused Talent",    pct: 2,  color: "64748B", desc: "员工智慧和经验未挖掘" }
];

const wcW = 5.8, wcH = 1.25;
wastes.forEach(function(w, i) {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const cx = col === 0 ? 0.35 : 7.15;
  const cy = 1.2 + row * 1.4;

  s4.addShape(pptx.ShapeType.rect, {
    x: cx, y: cy, w: wcW, h: wcH,
    fill: { color: "FFFFFF" },
    line: { color: "E2E8F0", width: 0.5 },
    rectRadius: 0.06
  });
  s4.addShape(pptx.ShapeType.rect, {
    x: cx, y: cy, w: 0.1, h: wcH,
    fill: { color: w.color }, line: { color: w.color, width: 0 }
  });
  s4.addShape(pptx.ShapeType.rect, {
    x: cx, y: cy + 0.1, w: 0.1, h: wcH - 0.2,
    fill: { color: w.color }, line: { color: w.color, width: 0 }
  });

  s4.addText(w.cn, {
    x: cx + 0.25, y: cy + 0.06, w: 2.0, h: 0.42,
    fontFace: "Arial Black", fontSize: 14, color: "1E2761",
    bold: true, valign: "middle"
  });
  s4.addText(w.en, {
    x: cx + 0.25, y: cy + 0.38, w: 2.2, h: 0.28,
    fontFace: "Arial", fontSize: 9, color: "94A3B8",
    valign: "middle"
  });
  s4.addText(w.desc, {
    x: cx + 0.25, y: cy + 0.64, w: 2.2, h: 0.35,
    fontFace: "Arial", fontSize: 10, color: "475569",
    valign: "middle"
  });

  const barX = cx + 2.8, barW = 2.5;
  s4.addShape(pptx.ShapeType.rect, {
    x: barX, y: cy + 0.18, w: barW, h: 0.2,
    fill: { color: "E2E8F0" }, line: { color: "E2E8F0", width: 0 },
    rectRadius: 0.04
  });
  const fillW = (w.pct / 35) * barW;
  s4.addShape(pptx.ShapeType.rect, {
    x: barX, y: cy + 0.18, w: fillW, h: 0.2,
    fill: { color: w.color }, line: { color: w.color, width: 0 },
    rectRadius: 0.04
  });
  s4.addText(w.pct + "%", {
    x: barX + barW + 0.1, y: cy + 0.08, w: 0.8, h: 0.4,
    fontFace: "Arial Black", fontSize: 14, color: w.color,
    bold: true, valign: "middle"
  });

  const sevLabel = w.pct >= 20 ? "严重" : (w.pct >= 8 ? "中等" : "一般");
  const sevColor = w.pct >= 20 ? "DC2626" : (w.pct >= 8 ? "F59E0B" : "0D9488");
  s4.addShape(pptx.ShapeType.roundRect, {
    x: cx + wcW - 0.8, y: cy + 0.15, w: 0.6, h: 0.28,
    fill: { color: sevColor }, transparency: 15,
    line: { color: sevColor, width: 0.5 },
    rectRadius: 0.06
  });
  s4.addText(sevLabel, {
    x: cx + wcW - 0.8, y: cy + 0.15, w: 0.6, h: 0.28,
    fontFace: "Arial Black", fontSize: 9, color: sevColor,
    align: "center", bold: true, valign: "middle"
  });
});

addFooter(s4, "制造业重点关注：过量生产、库存积压、搬运频繁");

// ============ SLIDE 5: 13+ TOOLS OVERVIEW ============
const s5 = pptx.addSlide();
setBg(s5);
addTopBar(s5, "0D9488");
addTitleBand(s5, "13+核心精益工具全景", "13+ Core Lean Tools Overview");

const tools = [
  { name: "看板",     en: "Kanban",        cat: "拉动系统", color: "0D9488" },
  { name: "VSM",      en: "Value Stream",  cat: "分析工具", color: "1E2761" },
  { name: "安灯",     en: "Andon",         cat: "现场管理", color: "DC2626" },
  { name: "标准作业", en: "Standard Work", cat: "标准化",   color: "0891B2" },
  { name: "TPM",      en: "TPM",           cat: "设备管理", color: "F59E0B" },
  { name: "5S",       en: "5S",            cat: "现场管理", color: "7C3AED" },
  { name: "改善",     en: "Kaizen",        cat: "持续改进", color: "0D9488" },
  { name: "平准化",   en: "Heijunka",      cat: "生产均衡", color: "1E2761" },
  { name: "防错",     en: "Poka-Yoke",     cat: "质量保障", color: "DC2626" },
  { name: "SMED",     en: "SMED",          cat: "快速换模", color: "0891B2" },
  { name: "自働化",   en: "Jidoka",        cat: "自动化",   color: "F59E0B" },
  { name: "JIT",      en: "JIT",           cat: "准时生产", color: "7C3AED" },
  { name: "可视化管理", en: "Visual Mgmt",  cat: "现场管理", color: "64748B" }
];

const tCardW = 3.0, tCardH = 1.45;
const tCols = 4;
const tStartX = 0.35, tStartY = 1.25;
const tGapX = 0.15, tGapY = 0.12;

tools.forEach(function(t, i) {
  const col = i % tCols;
  const row = Math.floor(i / tCols);
  const cx = tStartX + col * (tCardW + tGapX);
  const cy = tStartY + row * (tCardH + tGapY);

  s5.addShape(pptx.ShapeType.rect, {
    x: cx, y: cy, w: tCardW, h: tCardH,
    fill: { color: "FFFFFF" },
    line: { color: "E2E8F0", width: 0.5 },
    rectRadius: 0.06
  });

  // Top color bar
  s5.addShape(pptx.ShapeType.rect, {
    x: cx, y: cy, w: tCardW, h: 0.25,
    fill: { color: t.color }, line: { color: t.color, width: 0 },
    rectRadius: 0.06
  });
  // Fix bottom corners of top bar
  s5.addShape(pptx.ShapeType.rect, {
    x: cx, y: cy + 0.15, w: tCardW, h: 0.1,
    fill: { color: t.color }, line: { color: t.color, width: 0 }
  });

  // Category label
  s5.addText(t.cat, {
    x: cx, y: cy, w: tCardW, h: 0.25,
    fontFace: "Arial", fontSize: 8, color: "FFFFFF",
    align: "center", valign: "middle"
  });

  // Tool name (Chinese)
  s5.addText(t.name, {
    x: cx, y: cy + 0.35, w: tCardW, h: 0.45,
    fontFace: "Arial Black", fontSize: 14, color: "1E2761",
    align: "center", bold: true, valign: "middle"
  });

  // Tool name (English)
  s5.addText(t.en, {
    x: cx, y: cy + 0.72, w: tCardW, h: 0.3,
    fontFace: "Arial", fontSize: 9, color: "94A3B8",
    align: "center", valign: "middle"
  });

  // Bottom accent line
  s5.addShape(pptx.ShapeType.rect, {
    x: cx + 0.3, y: cy + tCardH - 0.12, w: tCardW - 0.6, h: 0.04,
    fill: { color: t.color }, line: { color: t.color, width: 0 }
  });
});

// "More" card at position 13
const moreCol = 3, moreRow = 3;
const moreX = tStartX + moreCol * (tCardW + tGapX);
const moreY = tStartY + moreRow * (tCardH + tGapY);
s5.addShape(pptx.ShapeType.rect, {
  x: moreX, y: moreY, w: tCardW, h: tCardH,
  fill: { color: "F1F5F9" },
  line: { color: "CBD5E1", width: 0.5 },
  rectRadius: 0.06
});
s5.addText("更多工具", {
  x: moreX, y: moreY + 0.3, w: tCardW, h: 0.4,
  fontFace: "Arial Black", fontSize: 14, color: "64748B",
  align: "center", bold: true, valign: "middle"
});
s5.addText("持续更新中...", {
  x: moreX, y: moreY + 0.65, w: tCardW, h: 0.3,
  fontFace: "Arial", fontSize: 10, color: "94A3B8",
  align: "center", valign: "middle"
});

addFooter(s5, "13 大核心工具 | 覆盖生产、质量、设备、物流全领域");

// ============ SLIDE 6: TOOL SELECTION DECISION TREE ============
const s6 = pptx.addSlide();
setBg(s6);
addTopBar(s6, "0D9488");
addTitleBand(s6, "工具选择决策树", "Tool Selection Decision Tree");

// Top: Question box
s6.addShape(pptx.ShapeType.roundRect, {
  x: 3.5, y: 1.2, w: 6.33, h: 0.9,
  fill: { color: "1E2761" },
  line: { color: "0D9488", width: 1 },
  rectRadius: 0.1
});
s6.addText("您面临的主要问题是什么？", {
  x: 3.5, y: 1.2, w: 6.33, h: 0.9,
  fontFace: "Arial Black", fontSize: 16, color: "FFFFFF",
  align: "center", bold: true, valign: "middle"
});

// Arrow down from question
s6.addShape(pptx.ShapeType.rect, {
  x: 6.5, y: 2.1, w: 0.06, h: 0.3,
  fill: { color: "0D9488" }, line: { color: "0D9488", width: 0 }
});
s6.addShape(pptx.ShapeType.downArrow, {
  x: 6.35, y: 2.35, w: 0.35, h: 0.3,
  fill: { color: "0D9488" }, line: { color: "0D9488", width: 0 }
});

// Level 2: 4 problem categories
const categories = [
  { label: "质量问题", sublabel: "Quality Issues", color: "DC2626", x: 0.35 },
  { label: "效率问题", sublabel: "Efficiency Issues", color: "F59E0B", x: 3.65 },
  { label: "库存问题", sublabel: "Inventory Issues", color: "0D9488", x: 6.95 },
  { label: "现场管理", sublabel: "Shop Floor Mgmt", color: "1E2761", x: 10.25 }
];
const catW = 2.8, catH = 0.85;

categories.forEach(function(cat) {
  // Connector line from center
  s6.addShape(pptx.ShapeType.rect, {
    x: cat.x + catW / 2 - 0.02, y: 2.6, w: 0.04, h: 0.15,
    fill: { color: cat.color }, line: { color: cat.color, width: 0 }
  });

  s6.addShape(pptx.ShapeType.roundRect, {
    x: cat.x, y: 2.75, w: catW, h: catH,
    fill: { color: cat.color },
    line: { color: cat.color, width: 0 },
    rectRadius: 0.08
  });
  s6.addText(cat.label, {
    x: cat.x, y: 2.78, w: catW, h: 0.45,
    fontFace: "Arial Black", fontSize: 13, color: "FFFFFF",
    align: "center", bold: true, valign: "middle"
  });
  s6.addText(cat.sublabel, {
    x: cat.x, y: 3.12, w: catW, h: 0.35,
    fontFace: "Arial", fontSize: 9, color: "FFFFFF",
    align: "center", valign: "middle"
  });
});

// Level 3: Tool recommendations
const recommendations = [
  { tools: ["防错 Poka-Yoke", "A3 报告", "标准作业"], parentColor: "DC2626", x: 0.35 },
  { tools: ["SMED", "VSM", "TPM"], parentColor: "F59E0B", x: 3.65 },
  { tools: ["看板 Kanban", "JIT", "平准化"], parentColor: "0D9488", x: 6.95 },
  { tools: ["5S", "安灯 Andon", "可视化管理"], parentColor: "1E2761", x: 10.25 }
];

recommendations.forEach(function(rec, ri) {
  const rx = rec.x;
  const catW2 = 2.8;

  // Connector
  s6.addShape(pptx.ShapeType.rect, {
    x: rx + catW2 / 2 - 0.02, y: 3.6, w: 0.04, h: 0.2,
    fill: { color: rec.parentColor }, line: { color: rec.parentColor, width: 0 }
  });

  // Tool boxes
  rec.tools.forEach(function(tool, ti) {
    const ty = 3.8 + ti * 0.62;
    const tW = catW2;

    s6.addShape(pptx.ShapeType.roundRect, {
      x: rx, y: ty, w: tW, h: 0.5,
      fill: { color: rec.parentColor }, transparency: 12,
      line: { color: rec.parentColor, width: 0.5 },
      rectRadius: 0.06
    });

    // Left mini bar
    s6.addShape(pptx.ShapeType.rect, {
      x: rx, y: ty + 0.08, w: 0.06, h: 0.34,
      fill: { color: rec.parentColor },
      line: { color: rec.parentColor, width: 0 }
    });

    s6.addText(tool, {
      x: rx + 0.12, y: ty, w: tW - 0.15, h: 0.5,
      fontFace: "Arial", fontSize: 10, color: "1E2761",
      valign: "middle"
    });
  });
});

// Bottom tip box
s6.addShape(pptx.ShapeType.roundRect, {
  x: 0.5, y: 6.0, w: W - 1.0, h: 0.65,
  fill: { color: "FEF3C7" },
  line: { color: "F59E0B", width: 0.5 },
  rectRadius: 0.08
});
s6.addText("提示：实际应用中，多种工具往往需要组合使用。建议从 5S 和可视化管理入手，逐步引入其他工具。", {
  x: 0.7, y: 6.0, w: W - 1.4, h: 0.65,
  fontFace: "Arial", fontSize: 11, color: "92400E",
  valign: "middle", wrap: true
});

addFooter(s6, "根据问题类型选择合适工具 | 组合使用效果更佳");

// ============ SAVE ============
pptx.writeFile({
  fileName: "./01-精益工具知识库\\PPT\\精益工具知识库-封面与目录.pptx"
}).then(function() {
  console.log("PPT file created successfully!");
}).catch(function(err) {
  console.error("Error:", err);
});
