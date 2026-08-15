/**
 * 精益工具知识库 - 主目录PPT
 * 离散制造企业精益转型核心知识库
 *
 * 使用方式: node 精益工具知识库-主目录.js
 */

const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.title = '精益工具知识库 - 离散制造企业精益转型';
pres.author = 'Lean Knowledge Base';
pres.subject = '精益生产 | 制造 | 精益转型';

// ============================================================
// 全局设计配置
// ============================================================
const COLORS = {
  primary: "1E2761",      // 深蓝 - 主色
  secondary: "CADCFC",    // 冰蓝 - 辅助色
  accent: "FFFFFF",       // 白色 - 强调
  dark: "0F172A",         // 深色背景
  light: "F8FAFC",        // 浅色背景
  text: "1E293B",         // 正文文字
  textLight: "64748B",    // 次要文字
  success: "059669",      // 成功/绿色
  warning: "D97706",      // 警告/橙色
  danger: "DC2626",       // 危险/红色
  teal: "0D9488",         // 青色
  tealLight: "5EEAD4",    // 浅青色
};

const FONT = {
  header: "Arial Black",
  body: "Arial",
};

// ============================================================
// 辅助函数
// ============================================================
function addDarkSlide(slide, title, subtitle) {
  slide.background = { color: COLORS.primary };
  // 顶部装饰条
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.08,
    fill: { color: COLORS.teal }
  });
  // 标题
  slide.addText(title, {
    x: 0.8, y: 1.5, w: 8.4, h: 1.2,
    fontSize: 36, fontFace: FONT.header, color: COLORS.accent,
    bold: true
  });
  // 副标题
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.8, y: 2.8, w: 8.4, h: 0.6,
      fontSize: 18, fontFace: FONT.body, color: COLORS.secondary
    });
  }
}

function addLightSlide(slide, title, options = {}) {
  slide.background = { color: COLORS.light };
  // 顶部装饰条
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.08,
    fill: { color: COLORS.primary }
  });
  // 标题区域背景
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0.08, w: 10, h: 0.85,
    fill: { color: COLORS.primary }
  });
  // 标题
  slide.addText(title, {
    x: 0.8, y: 0.15, w: 8.4, h: 0.65,
    fontSize: 28, fontFace: FONT.header, color: COLORS.accent,
    bold: true, margin: 0
  });
  if (options.subtitle) {
    slide.addText(options.subtitle, {
      x: 0.8, y: 0.55, w: 8.4, h: 0.3,
      fontSize: 14, fontFace: FONT.body, color: COLORS.secondary,
      margin: 0
    });
  }
}

function addStatCard(slide, x, y, number, label, color = COLORS.teal) {
  // 卡片背景
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 2.8, h: 1.5,
    fill: { color: "FFFFFF" },
    shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.1 }
  });
  // 左侧装饰条
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.08, h: 1.5,
    fill: { color }
  });
  // 大数字
  slide.addText(number, {
    x: x + 0.3, y: y + 0.2, w: 2.3, h: 0.7,
    fontSize: 32, fontFace: FONT.header, color: COLORS.primary,
    bold: true, align: "center"
  });
  // 标签
  slide.addText(label, {
    x: x + 0.2, y: y + 0.95, w: 2.5, h: 0.4,
    fontSize: 11, fontFace: FONT.body, color: COLORS.textLight,
    align: "center"
  });
}

function addTwoColumnCard(slide, x, y, w, h, header, items, headerColor = COLORS.primary) {
  // 卡片背景
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: "FFFFFF" },
    shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 135, opacity: 0.08 }
  });
  // 顶部色条
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h: 0.35,
    fill: { color: headerColor }
  });
  // 标题
  slide.addText(header, {
    x: x + 0.2, y: y + 0.05, w: w - 0.4, h: 0.28,
    fontSize: 13, fontFace: FONT.header, color: COLORS.accent,
    bold: true, margin: 0, valign: "middle"
  });
  // 列表项
  items.forEach((item, i) => {
    slide.addText([
      { text: item, options: { bullet: true, breakLine: i < items.length - 1 } }
    ], {
      x: x + 0.2, y: y + 0.42 + i * 0.28, w: w - 0.4, h: 0.28,
      fontSize: 10, fontFace: FONT.body, color: COLORS.text,
      margin: 0
    });
  });
}

function addProcessFlow(slide, x, y, w, steps, color = COLORS.teal) {
  const stepW = (w - (steps.length - 1) * 0.15) / steps.length;
  steps.forEach((step, i) => {
    const sx = x + i * (stepW + 0.15);
    // 步骤框
    slide.addShape(pres.shapes.RECTANGLE, {
      x: sx, y, w: stepW, h: 0.9,
      fill: { color }, rectRadius: 0.05
    });
    // 步骤文字
    slide.addText(step, {
      x: sx, y: 0.1, w: stepW, h: 0.7,
      fontSize: 10, fontFace: FONT.body, color: COLORS.accent,
      align: "center", valign: "middle", bold: true
    });
    // 箭头（非最后一步）
    if (i < steps.length - 1) {
      slide.addShape(pres.shapes.LINE, {
        x: sx + stepW + 0.02, y: 0.35, w: 0.11, h: 0,
        line: { color: COLORS.textLight, width: 2 }
      });
    }
  });
}

// ============================================================
// 幻灯片 1: 封面
// ============================================================
let slide1 = pres.addSlide();
slide1.background = { color: COLORS.primary };

// 顶部装饰线
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 0.12,
  fill: { color: COLORS.teal }
});

// 右侧装饰几何
slide1.addShape(pres.shapes.RECTANGLE, {
  x: 8.5, y: 0, w: 1.5, h: 5.625,
  fill: { color: COLORS.dark, transparency: 30 }
});

// 主标题
slide1.addText("精益工具知识库", {
  x: 0.8, y: 1.2, w: 7.5, h: 1.2,
  fontSize: 44, fontFace: FONT.header, color: COLORS.accent,
  bold: true
});

// 副标题
slide1.addText("离散制造企业精益转型核心指南", {
  x: 0.8, y: 2.5, w: 7, h: 0.6,
  fontSize: 20, fontFace: FONT.body, color: COLORS.secondary
});

// 分隔线
slide1.addShape(pres.shapes.LINE, {
  x: 0.8, y: 3.3, w: 3, h: 0,
  line: { color: COLORS.teal, width: 3 }
});

// 关键数据点
const coverStats = [
  { num: "13+", label: "核心精益工具" },
  { num: "5", label: "问题解决方法" },
  { num: "4", label: "深度专题研究" },
  { num: "70%", label: "转型失败率*" },
];

coverStats.forEach((s, i) => {
  const sx = 0.8 + i * 2.2;
  slide1.addText(s.num, {
    x: sx, y: 3.8, w: 2, h: 0.5,
    fontSize: 28, fontFace: FONT.header, color: COLORS.tealLight,
    bold: true
  });
  slide1.addText(s.label, {
    x: sx, y: 4.35, w: 2, h: 0.3,
    fontSize: 10, fontFace: FONT.body, color: COLORS.secondary
  });
});

// 底部注释
slide1.addText("* 精益转型失败率高达70%，根本原因在于变革管理而非工具技术", {
  x: 0.8, y: 5.1, w: 8, h: 0.3,
  fontSize: 9, fontFace: FONT.body, color: COLORS.textLight
});

// ============================================================
// 幻灯片 2: 目录
// ============================================================
let slide2 = pres.addSlide();
addLightSlide(slide2, "知识库目录", { subtitle: "Contents" });

const tocItems = [
  { num: "01", title: "精益基础", desc: "精益哲学 · 八大浪费 · TPS体系 · 术语表", color: COLORS.primary },
  { num: "02", title: "核心工具（13+）", desc: "看板 · VSM · 安灯 · 标准作业 · TPM · 5S · 改善 · 平准化 · 防错 · SMED · 自働化 · JIT · 可视化管理", color: COLORS.teal },
  { num: "03", title: "问题解决方法", desc: "Gemba Walk · A3 · PDCA · DMAIC · VA/VE", color: COLORS.success },
  { num: "04", title: "制造工序应用", desc: "机加工 · 精加工 · 热处理 · 表面处理 · 包装", color: COLORS.warning },
  { num: "05", title: "实践案例集", desc: "SMED改善案例 · 改善提案模板 · 实施指南", color: COLORS.danger },
  { num: "06", title: "深度专题研究", desc: "变革管理 · VSM高级实战 · 质量标准整合 · 精益数字化", color: COLORS.primary },
];

tocItems.forEach((item, i) => {
  const row = Math.floor(i / 2);
  const col = i % 2;
  const x = 0.5 + col * 4.7;
  const y = 1.2 + row * 1.35;

  // 卡片背景
  slide2.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 4.4, h: 1.2,
    fill: { color: "FFFFFF" },
    shadow: { type: "outer", color: "000000", blur: 4, offset: 1, angle: 135, opacity: 0.08 }
  });
  // 左侧色条
  slide2.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.1, h: 1.2,
    fill: { color: item.color }
  });
  // 编号
  slide2.addText(item.num, {
    x: x + 0.25, y: y + 0.1, w: 0.6, h: 0.4,
    fontSize: 18, fontFace: FONT.header, color: item.color,
    bold: true
  });
  // 标题
  slide2.addText(item.title, {
    x: x + 0.85, y: y + 0.12, w: 3.3, h: 0.35,
    fontSize: 14, fontFace: FONT.header, color: COLORS.text,
    bold: true, margin: 0
  });
  // 描述
  slide2.addText(item.desc, {
    x: x + 0.25, y: y + 0.5, w: 4, h: 0.55,
    fontSize: 9, fontFace: FONT.body, color: COLORS.textLight
  });
});

// ============================================================
// 幻灯片 3: 精益哲学与原则
// ============================================================
let slide3 = pres.addSlide();
addLightSlide(slide3, "精益哲学与原则", { subtitle: "Lean Philosophy & Principles" });

// 五大原则
const principles = [
  { name: "价值 Value", desc: "从客户视角定义价值", icon: "◎" },
  { name: "价值流 Value Stream", desc: "识别端到端价值流", icon: "⇒" },
  { name: "流动 Flow", desc: "让价值持续流动", icon: "▶" },
  { name: "拉动 Pull", desc: "由需求驱动生产", icon: "◀" },
  { name: "尽善尽美 Perfection", desc: "追求永无止境的改进", icon: "∞" },
];

principles.forEach((p, i) => {
  const x = 0.5 + i * 1.9;
  // 圆形背景
  slide3.addShape(pres.shapes.OVAL, {
    x: x + 0.3, y: 1.3, w: 1.2, h: 1.2,
    fill: { color: COLORS.primary }
  });
  slide3.addText(p.icon, {
    x: x + 0.3, y: 1.45, w: 1.2, h: 0.6,
    fontSize: 28, fontFace: FONT.body, color: COLORS.accent,
    align: "center", valign: "middle"
  });
  slide3.addText(p.name, {
    x: x, y: 2.6, w: 1.8, h: 0.4,
    fontSize: 11, fontFace: FONT.header, color: COLORS.text,
    align: "center", bold: true
  });
  slide3.addText(p.desc, {
    x: x, y: 3.0, w: 1.8, h: 0.4,
    fontSize: 9, fontFace: FONT.body, color: COLORS.textLight,
    align: "center"
  });
});

// 核心理念卡片
slide3.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 3.7, w: 9, h: 1.5,
  fill: { color: COLORS.primary, transparency: 5 }
});

slide3.addText("精益核心理念", {
  x: 0.8, y: 3.8, w: 3, h: 0.35,
  fontSize: 14, fontFace: FONT.header, color: COLORS.primary,
  bold: true
});

const coreValues = [
  "消除浪费（Muda）",
  "尊重人性（Respect for People）",
  "持续改善（Kaizen）",
  "现地现物（Genchi Genbutsu）"
];

coreValues.forEach((v, i) => {
  const col = Math.floor(i / 2);
  const row = i % 2;
  slide3.addText([
    { text: v, options: { bullet: true, breakLine: row === 0 && i < 2 } }
  ], {
    x: 0.8 + col * 4.5, y: 4.2 + row * 0.35, w: 4.2, h: 0.35,
    fontSize: 11, fontFace: FONT.body, color: COLORS.text
  });
});

// ============================================================
// 幻灯片 4: 八大浪费
// ============================================================
let slide4 = pres.addSlide();
addLightSlide(slide4, "八大浪费识别指南", { subtitle: "8 Wastes (Muda)" });

const wastes = [
  { name: "过量生产", en: "Overproduction", desc: "超出需求的生产", color: COLORS.danger, pct: "35%" },
  { name: "等待", en: "Waiting", desc: "人员/设备空闲", color: COLORS.warning, pct: "20%" },
  { name: "搬运", en: "Transportation", desc: "不必要的物料移动", color: COLORS.warning, pct: "10%" },
  { name: "过度加工", en: "Over-processing", desc: "超出客户要求的加工", color: COLORS.teal, pct: "8%" },
  { name: "库存", en: "Inventory", desc: "过量原材料/WIP/成品", color: COLORS.primary, pct: "15%" },
  { name: "动作", en: "Motion", desc: "人员不必要的动作", color: COLORS.teal, pct: "5%" },
  { name: "不良品", en: "Defects", desc: "不合格品和返工", color: COLORS.danger, pct: "5%" },
  { name: "未利用人才", en: "Unused Talent", desc: "员工智慧未被发挥", color: COLORS.success, pct: "2%" },
];

wastes.forEach((w, i) => {
  const col = Math.floor(i / 4);
  const row = i % 4;
  const x = 0.5 + col * 4.8;
  const y = 1.2 + row * 1.05;

  // 卡片
  slide4.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 4.5, h: 0.9,
    fill: { color: "FFFFFF" },
    shadow: { type: "outer", color: "000000", blur: 3, offset: 1, angle: 135, opacity: 0.06 }
  });
  // 左侧色条
  slide4.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.08, h: 0.9,
    fill: { color: w.color }
  });
  // 浪费名称
  slide4.addText(w.name, {
    x: x + 0.2, y: y + 0.08, w: 2, h: 0.3,
    fontSize: 12, fontFace: FONT.header, color: COLORS.text,
    bold: true, margin: 0
  });
  // 英文名
  slide4.addText(w.en, {
    x: x + 2.2, y: y + 0.1, w: 1.5, h: 0.25,
    fontSize: 9, fontFace: FONT.body, color: COLORS.textLight,
    margin: 0
  });
  // 描述
  slide4.addText(w.desc, {
    x: x + 0.2, y: y + 0.38, w: 3, h: 0.25,
    fontSize: 9, fontFace: FONT.body, color: COLORS.text,
    margin: 0
  });
  // 占比
  slide4.addText(w.pct, {
    x: x + 3.6, y: y + 0.2, w: 0.7, h: 0.4,
    fontSize: 16, fontFace: FONT.header, color: w.color,
    bold: true, align: "center"
  });
});

// ============================================================
// 幻灯片 5: 核心工具全景图
// ============================================================
let slide5 = pres.addSlide();
addLightSlide(slide5, "13+核心精益工具全景", { subtitle: "Core Lean Tools Overview" });

const tools = [
  { name: "看板", en: "Kanban", cat: "拉动", color: COLORS.primary },
  { name: "VSM", en: "Value Stream Map", cat: "分析", color: COLORS.teal },
  { name: "安灯", en: "Andon", cat: "响应", color: COLORS.danger },
  { name: "标准作业", en: "Standard Work", cat: "基础", color: COLORS.success },
  { name: "TPM", en: "Total Prod. Maintenance", cat: "设备", color: COLORS.warning },
  { name: "5S", en: "5S Workplace Org.", cat: "基础", color: COLORS.primary },
  { name: "改善", en: "Kaizen", cat: "文化", color: COLORS.teal },
  { name: "平准化", en: "Heijunka", cat: "均衡", color: COLORS.success },
  { name: "防错", en: "Poka-Yoke", cat: "质量", color: COLORS.danger },
  { name: "SMED", en: "Quick Changeover", cat: "效率", color: COLORS.warning },
  { name: "自働化", en: "Jidoka", cat: "质量", color: COLORS.primary },
  { name: "JIT", en: "Just-In-Time", cat: "流动", color: COLORS.teal },
  { name: "可视化", en: "Visual Management", cat: "基础", color: COLORS.success },
];

tools.forEach((t, i) => {
  const col = i % 4;
  const row = Math.floor(i / 4);
  const x = 0.4 + col * 2.4;
  const y = 1.2 + row * 1.4;

  // 工具卡片
  slide5.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 2.2, h: 1.2,
    fill: { color: "FFFFFF" },
    shadow: { type: "outer", color: "000000", blur: 3, offset: 1, angle: 135, opacity: 0.06 }
  });
  // 顶部色条
  slide5.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 2.2, h: 0.25,
    fill: { color: t.color }
  });
  // 类别标签
  slide5.addText(t.cat, {
    x: x + 0.1, y: y + 0.03, w: 2, h: 0.2,
    fontSize: 8, fontFace: FONT.body, color: COLORS.accent,
    align: "center", margin: 0
  });
  // 工具名
  slide5.addText(t.name, {
    x: x + 0.1, y: y + 0.35, w: 2, h: 0.35,
    fontSize: 13, fontFace: FONT.header, color: COLORS.text,
    bold: true, align: "center", margin: 0
  });
  // 英文名
  slide5.addText(t.en, {
    x: x + 0.1, y: y + 0.7, w: 2, h: 0.25,
    fontSize: 8, fontFace: FONT.body, color: COLORS.textLight,
    align: "center", margin: 0
  });
});

// ============================================================
// 幻灯片 6: 工具选择决策树
// ============================================================
let slide6 = pres.addSlide();
addLightSlide(slide6, "工具选择决策树", { subtitle: "Tool Selection Decision Tree" });

// 决策流程
const decisionSteps = [
  { q: "问题类型识别", y: 1.3 },
  { q: "质量 → 防错+标准作业+安灯+A3", y: 2.0, color: COLORS.danger },
  { q: "效率 → VSM+SMED+TPM+改善", y: 2.6, color: COLORS.warning },
  { q: "库存