const PptxGenJS = require("pptxgenjs");
const path = require("path");
const OUT = __dirname;

let pptx = new PptxGenJS();
pptx.layout = "LAYOUT_WIDE";
pptx.title = "防错与SMED详解 Poka-Yoke & SMED";
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

// SLIDE 01: Cover
(function(){var s=pptx.addSlide();s.background={color:C.P};s.addShape(S.ellipse,{x:9.5,y:-1.5,w:6.5,h:6.5,fill:{color:"1B2D6B"},line:{color:"000000"}});s.addShape(S.ellipse,{x:10.5,y:-.5,w:4.5,h:4.5,fill:{color:"233B7A"},line:{color:"000000"}});s.addText("05",{x:.8,y:1,w:4,h:2.8,fontFace:"Arial",fontSize:100,color:C.S,bold:true});s.addShape(S.rect,{x:.8,y:3.6,w:3.2,h:.06,fill:{color:C.G},line:{color:"000000"}});s.addText("防错与SMED详解",{x:.8,y:3.8,w:8.5,h:1.2,fontFace:"Microsoft YaHei",fontSize:44,color:C.A,bold:true,valign:"middle"});s.addText("Poka-Yoke & SMED",{x:.8,y:4.65,w:8,h:.6,fontFace:"Arial",fontSize:20,color:C.S});s.addText("从错误预防到快速换模\n连接件制造的精益利器",{x:.8,y:5.45,w:8,h:1,fontFace:"Microsoft YaHei",fontSize:14,color:C.TL})})();

// SLIDE 02: Types
(function(){var s=pptx.addSlide();setBg(s);addTopBar(s,C.G);addTitleBand(s,"防错原理与类型","Principles & Types of Poka-Yoke");addFooter(s,"05 | 防错与SMED详解 | 防错原理与类型");sectLabel(s,"PART 1 · 防错");
cardB(s,.5,1.78,3.9,2.55,C.G,[{t:"① 接触法  Contact Method",y:.08,size:11.5,bold:true,color:C.P},{t:"通过物理接触检测产品形状/尺寸缺陷\n如：限位针、检具、模具定位块",y:.45,size:10,color:C.TL},{t:"② 定值法  Fixed-Value Method",y:.95,size:11.5,bold:true,color:C.P},{t:"确保操作次数/数量正确\n如：计数器、称重检测、限位开关计数",y:1.32,size:10,color:C.TL},{t:"③ 动作步骤法  Motion-Step",y:1.82,size:11.5,bold:true,color:C.P},{t:"检测动作顺序是否正确\n如：顺序锁定装置、互锁机构",y:2.19,size:10,color:C.TL}]);
cardB(s,.5,4.53,3.9,2.2,C.TE,[{t:"④ 成组法  Grouping Method",y:.08,size:11.5,bold:true,color:C.P},{t:"防止混料/错料\n如：颜色标识、料斗分格、条码/RFID检测",y:.45,size:10,color:C.TL},{t:"将多个防错点集中到组合式检测站\n实现多件并行防错，提升效率",y:1.18,size:10,color:C.TL}]);
var tx=4.65,tw=[2,2.74,2.8];th(s,tx,1.78,tw,["对比维度","传统检验","防错 Poka-Yoke"]);
var tR=[["发现时机","事后检验","事前预防"],["拦截能力","可能漏检","100% 阻止"],["依赖度","依赖人员技能","不依赖人员判断"],["成本","额外检验工序","装置投入，长期节省"],["响应速度","慢（迟批问题）","即时（单件阻止）"],["改善方式","被动接受","主动消除根因"]];
for(var i=0;i<tR.length;i++)tr(s,tx,2.22+i*.44,tw,tR[i],i%2===0?C.A:C.L,C.TL,C.W,C.G);
s.addShape(S.roundRect,{x:tx,y:5,w:3.9,h:.38,fill:{color:C.G},rectRadius:.19,line:{color:C.G}});s.addText("预防级 Prevention",{x:tx,y:5,w:3.9,h:.38,fontFace:"Microsoft YaHei",fontSize:11,color:C.A,align:"center",valign:"middle",bold:true});s.addText("在错误发生前消除根本原因",{x:tx,y:5.42,w:3.9,h:.35,fontFace:"Microsoft YaHei",fontSize:9,color:C.TL,align:"center",valign:"middle"});
s.addShape(S.roundRect,{x:tx+4.28,y:5,w:3.9,h:.38,fill:{color:C.W},rectRadius:.19,line:{color:C.W}});s.addText("检测级 Detection",{x:tx+4.28,y:5,w:3.9,h:.38,fontFace:"Microsoft YaHei",fontSize:11,color:C.A,align:"center",valign:"middle",bold:true});s.addText("在错误发生后立即检测拦截",{x:tx+4.28,y:5.42,w:3.9,h:.35,fontFace:"Microsoft YaHei",fontSize:9,color:C.TL,align:"center",valign:"middle"});
s.addShape(S.rightArrow,{x:tx+3.9,y:5.05,w:.38,h:.28,fill:{color:C.TL},line:{color:C.TL}})})();

// SLIDE 03: Cases
(function(){var s=pptx.addSlide();setBg(s);addTopBar(s,C.G);addTitleBand(s,"防错装置案例","Poka-Yoke Devices in Discrete Manufacturing");addFooter(s,"05 | 防错与SMED详解 | 防错装置案例");sectLabel(s,"连接件制造 · 实战案例");
cardB(s,.5,1.78,3.9,2.55,C.G,[{t:"案例1：错误模具检测",y:.08,size:12,bold:true,color:C.P},{t:"问题：换模时装错模具导致批量废品",y:.42,size:10,color:C.TL},{t:"方案：模具定位销+接近传感器联动",y:.72,size:10,color:C.TL},{t:"效果：错误安装100%检测并报警停机",y:1.02,size:10,color:C.TL},{t:"防错类型：接触法+定值法",y:1.32,size:9.5,color:C.TE},{t:"Zero Defect Since 2021",y:1.85,size:10,bold:true,color:C.G}]);
cardB(s,4.7,1.78,3.9,2.55,C.TE,[{t:"案例2：漏尺寸检测",y:.08,size:12,bold:true,color:C.P},{t:"问题：加工工序漏加工尺寸流出",y:.42,size:10,color:C.TL},{t:"方案：量规在线自动检测装置",y:.72,size:10,color:C.TL},{t:"效果：每件自动检测，NG品自动排出",y:1.02,size:10,color:C.TL},{t:"防错类型：接触法+动作步骤法",y:1.32,size:9.5,color:C.TE},{t:"Detection at Every Piece",y:1.85,size:10,bold:true,color:C.TE}]);
cardB(s,8.9,1.78,3.93,2.55,C.W,[{t:"案例3：材料混料检测",y:.08,size:12,bold:true,color:C.P},{t:"问题：不同钢号（304 vs 316）混料",y:.42,size:10,color:C.TL},{t:"方案：激光光谱在线识别+自动分流",y:.72,size:10,color:C.TL},{t:"效果：实时识别，自动分流至对应料仓",y:1.02,size:10,color:C.TL},{t:"防错类型：成组法",y:1.32,size:9.5,color:C.TE},{t:"Material Mix-up Prevented",y:1.85,size:10,bold:true,color:C.W}]);
cardB(s,2.6,4.60,8.13,2.15,C.D,[{t:"案例4：包装混装防错  Mix-up Prevention",y:.08,size:12,bold:true,color:C.P},{t:"问题：不同规格工件（某型号 vs 某型号）混装出货",y:.42,size:10,color:C.TL},{t:"方案：自动称重扫码系统+条码双重校验",y:.72,size:10,color:C.TL},{t:"效果：错装出货次数降为零；视频联动拍照存档",y:1.02,size:10,color:C.TL},{t:"称重精度：±0.1g   扫码速度：<1秒   追溯保存：3年+",y:1.45,size:9.5,bold:true,color:C.D}]);
s.addShape(S.diamond,{x:6,y:4.15,w:1.33,h:.85,fill:{color:"EEF2FF"},line:{color:C.P}});s.addText("均属于",{x:6,y:4.2,w:1.33,h:.75,fontFace:"Microsoft YaHei",fontSize:10,color:C.P,align:"center",valign:"middle",bold:true})})();

// SLIDE 04: Implementation
(function(){var s=pptx.addSlide();setBg(s);addTopBar(s,C.G);addTitleBand(s,"防错实施方法论","7-Step Poka-Yoke Implementation");addFooter(s,"05 | 防错与SMED详解 | 防错实施方法论");sectLabel(s,"七步法 · 零成本优先");
var steps=[{n:"1",t:"识别缺陷",d:"记录缺陷类型和发生频率"},{n:"2",t:"分析原因",d:"5Why分析找到根本原因"},{n:"3",t:"设计对策",d:"选择防错类型和方案"},{n:"4",t:"零成本优先",d:"利用重力/限位/颜色标识"},{n:"5",t:"制作装置",d:"快速原型试运行验证"},{n:"6",t:"培训执行",d:"操作员参与标准化"},{n:"7",t:"持续改善",d:"定期评估完善迭代"}];
var sw=1.55,sh=.90,gap=.12,sx=.4,sy=1.95;
for(var i=0;i<steps.length;i++){var st=steps[i];var x=sx+i*(sw+gap);var cl=i<3?C.G:(i<5?C.TE:C.P);var cx=x+sw/2-.22;
s.addShape(S.ellipse,{x:cx,y:sy,w:.44,h:.44,fill:{color:cl},line:{color:cl}});s.addText(st.n,{x:cx,y:sy,w:.44,h:.44,fontFace:"Arial",fontSize:16,color:C.A,bold:true,align:"center",valign:"middle"});
s.addShape(S.roundRect,{x:x,y:sy+.52,w:sw,h:.52,fill:{color:"F1F5F9"},rectRadius:.08,line:{color:cl}});s.addText(st.t,{x:x+.05,y:sy+.52,w:sw-.1,h:.32,fontFace:"Microsoft YaHei",fontSize:10,color:C.T,bold:true,align:"center",valign:"middle"});s.addText(st.d,{x:x+.05,y:sy+.72,w:sw-.1,h:.28,fontFace:"Microsoft YaHei",fontSize:7,color:C.TL,align:"center",valign:"middle"});
if(i<steps.length-1)s.addShape(S.rightArrow,{x:x+sw+.02,y:sy+.20,w:gap-.04,h:.24,fill:{color:C.TL},line:{color:C.TL}})}
s.addShape(S.rect,{x:.4,y:3.15,w:12.53,h:.06,fill:{color:C.G},line:{color:"000000"}});
s.addText("零成本防错优先原则：先用最简单的方法（重力、限位、颜色）解决问题",{x:.4,y:3.25,w:12.53,h:.4,fontFace:"Microsoft YaHei",fontSize:11,color:C.TL,align:"center",valign:"middle"});
s.addShape(S.ellipse,{x:3.5,y:3.8,w:1.8,h:.85,fill:{color:C.TE},line:{color:C.TE}});s.addText("操作员\n全员参与",{x:3.5,y:3.8,w:1.8,h:.85,fontFace:"Microsoft YaHei",fontSize:11,color:C.A,bold:true,align:"center",valign:"middle"});
s.addShape(S.ellipse,{x:7.2,y:3.8,w:1.8,h:.85,fill:{color:C.G},line:{color:C.G}});s.addText("快速验证\n循环迭代",{x:7.2,y:3.8,w:1.8,h:.85,fontFace:"Microsoft YaHei",fontSize:11,color:C.A,bold:true,align:"center",valign:"middle"});
s.addText("操作员是防错的第一责任人——他们最了解现场问题",{x:2.4,y:4.8,w:8.53,h:.4,fontFace:"Microsoft YaHei",fontSize:10,color:C.TL,align:"center",valign:"middle"})})();

// SLIDE 05: SMED Three Stages
(function(){var s=pptx.addSlide();setBg(s);addTopBar(s,C.TE);addTitleBand(s,"SMED 三步法","Single Minute Exchange of Die");addFooter(s,"05 | 防错与SMED详解 | SMED 三步法");sectLabel(s,"PART 2 · SMED");
var bx=1.2,by=1.85,bw=2.8,bh=1.4;
s.addShape(S.roundRect,{x:bx,y:by,w:bw,h:bh,fill:{color:C.P},rectRadius:.12,line:{color:C.P}});s.addText("第一步",{x:bx,y:by+.08,w:bw,h:.25,fontFace:"Microsoft YaHei",fontSize:9,color:C.S,align:"center",valign:"middle"});s.addText("区分内部与外部",{x:bx,y:by+.3,w:bw,h:.35,fontFace:"Microsoft YaHei",fontSize:13,color:C.A,bold:true,align:"center",valign:"middle"});s.addText("Internal vs External\n区分必须停机\n才能完成的操作",{x:bx,y:by+.65,w:bw,h:.55,fontFace:"Microsoft YaHei",fontSize:8.5,color:C.S,align:"center",valign:"middle"});
s.addShape(S.rightArrow,{x:bw+1.2+.05,y:by+.5,w:.4,h:.4,fill:{color:C.G},line:{color:C.G}});
s.addShape(S.roundRect,{x:bx+bw+.45,y:by,w:bw,h:bh,fill:{color:C.G},rectRadius:.12,line:{color:C.G}});s.addText("第二步",{x:bx+bw+.45,y:by+.08,w:bw,h:.25,fontFace:"Microsoft YaHei",fontSize:9,color:C.A,align:"center",valign:"middle"});s.addText("转化内部为外部",{x:bx+bw+.45,y:by+.3,w:bw,h:.35,fontFace:"Microsoft YaHei",fontSize:13,color:C.A,bold:true,align:"center",valign:"middle"});s.addText("Convert to External\n将停机操作转化\n为可提前准备",{x:bx+bw+.45,y:by+.65,w:bw,h:.55,fontFace:"Microsoft YaHei",fontSize:8.5,color:C.A,align:"center",valign:"middle"});
s.addShape(S.rightArrow,{x:bw*2+.85+.05,y:by+.5,w:.4,h:.4,fill:{color:C.G},line:{color:C.G}});
s.addShape(S.roundRect,{x:bx+bw*2+.85,y:by,w:2.9,h:bh,fill:{color:C.TE},rectRadius:.12,line:{color:C.TE}});s.addText("第三步",{x:bx+bw*2+.85,y:by+.08,w:2.9,h:.25,fontFace:"Microsoft YaHei",fontSize:9,color:C.A,align:"center",valign:"middle"});s.addText("优化所有操作",{x:bx+bw*2+.85,y:by+.3,w:2.9,h:.35,fontFace:"Microsoft YaHei",fontSize:13,color:C.A,bold:true,align:"center",valign:"middle"});s.addText("Streamline All\n简化剩余操作\n目标：<10分钟",{x:bx+bw*2+.85,y:by+.65,w:2.9,h:.55,fontFace:"Microsoft YaHei",fontSize:8.5,color:C.A,align:"center",valign:"middle"});
// Bottom transformation bar chart
var dy=3.6;
s.addShape(S.rect,{x:.5,y:dy,w:12.33,h:.06,fill:{color:C.G},line:{color:"000000"}});
s.addText("换模时间压缩示意：从 60 分钟压缩至 <10 分钟",{x:.5,y:dy+.1,w:12.33,h:.3,fontFace:"Microsoft YaHei",fontSize:10,color:C.TL,align:"center",valign:"middle"});
s.addShape(S.rect,{x:1,y:dy+.5,w:11.33,h:.5,fill:{color:"FEE2E2"},line:{color:"000000"}});s.addShape(S.rect,{x:1,y:dy+.5,w:8,h:.5,fill:{color:C.D},line:{color:"000000"}});s.addText("换前 Internal 50min  |  换后 External 10min",{x:1,y:dy+.5,w:11.33,h:.5,fontFace:"Microsoft YaHei",fontSize:11,color:C.A,bold:true,align:"center",valign:"middle"});
s.addShape(S.rect,{x:1,y:dy+1.15,w:11.33,h:.5,fill:{color:"ECFDF5"},line:{color:"000000"}});s.addShape(S.rect,{x:1,y:dy+1.15,w:1.5,h:.5,fill:{color:C.G},line:{color:"000000"}});s.addText("换前 Internal <10min（目标）  |  外部准备已全部完成",{x:1,y:dy+1.15,w:11.33,h:.5,fontFace:"Microsoft YaHei",fontSize:11,color:C.G,bold:true,align:"center",valign:"middle"});
s.addText("压缩率 >80%",{x:1,y:dy+1.75,w:11.33,h:.3,fontFace:"Microsoft YaHei",fontSize:18,color:C.G,bold:true,align:"center",valign:"middle"})})();

// SLIDE 06: SMED Manufacturing Case Study
(function(){var s=pptx.addSlide();setBg(s);addTopBar(s,C.TE);addTitleBand(s,"SMED 连接件案例","Machining Die Change: 60min → <10min");addFooter(s,"05 | 防错与SMED详解 | SMED 连接件案例");sectLabel(s,"机加工模换模改善实例");
// Before/After columns
// Before header
s.addShape(S.rect,{x:.5,y:1.78,w:5.9,h:.44,fill:{color:C.D},line:{color:C.D}});s.addText("改善前 BEFORE（合计 60 分钟）",{x:.5,y:1.78,w:5.9,h:.44,fontFace:"Microsoft YaHei",fontSize:13,color:C.A,bold:true,align:"center",valign:"middle"});
// After header
s.addShape(S.rect,{x:6.9,y:1.78,w:5.93,h:.44,fill:{color:C.G},line:{color:C.G}});s.addText("改善后 AFTER（合计 <10 分钟）",{x:6.9,y:1.78,w:5.93,h:.44,fontFace:"Microsoft YaHei",fontSize:13,color:C.A,bold:true,align:"center",valign:"middle"});
var beforeSteps=[["1.停机确认模具型号","8 分钟","内部","需停机"],["2.拆卸旧模具","12 分钟","内部","需停机"],["3.搬运新模具到机台","10 分钟","内部","需停机"],["4.安装新模具","15 分钟","内部","需停机"],["5.调试与试生产","15 分钟","内部","需停机"]];
var afterSteps=[["1.提前备好模具与工具","0 分钟","外部","换线前完成"],["2.模具预热（提前启动）","0 分钟","外部","换线前完成"],["3.快速定位安装模具","3 分钟","内部","标准化定位"],["4.一键参数调用","2 分钟","内部","参数预存"],["5.首件确认与生产","4 分钟","内部","减少试模"]];
for(var i=0;i<beforeSteps.length;i++){var row=beforeSteps[i];var ry=2.22+i*.68;
s.addShape(S.rect,{x:.5,y:ry,w:5.9,h:.65,fill:{color:i%2===0?C.A:"FEF2F2"},line:{color:"CBD5E1"}});
s.addText(row[0],{x:.6,y:ry,w:3.2,h:.65,fontFace:"Microsoft YaHei",fontSize:10,color:C.T,valign:"middle"});
s.addText(row[1],{x:3.8,y:ry,w:1.2,h:.65,fontFace:"Arial",fontSize:11,color:C.D,bold:true,align:"center",valign:"middle"});
s.addText(row[2],{x:5.0,y:ry,w:.9,h:.65,fontFace:"Microsoft YaHei",fontSize:9,color:C.W,align:"center",valign:"middle"})}
for(var i=0;i<afterSteps.length;i++){var row=afterSteps[i];var ry=2.22+i*.68;
s.addShape(S.rect,{x:6.9,y:ry,w:5.93,h:.65,fill:{color:i%2===0?C.A:"F0FDF4"},line:{color:"CBD5E1"}});
s.addText(row[0],{x:7.0,y:ry,w:3.3,h:.65,fontFace:"Microsoft YaHei",fontSize:10,color:C.T,valign:"middle"});
s.addText(row[1],{x:10.3,y:ry,w:1.1,h:.65,fontFace:"Arial",fontSize:11,color:C.G,bold:true,align:"center",valign:"middle"});
s.addText(row[2],{x:11.4,y:ry,w:1.2,h:.65,fontFace:"Microsoft YaHei",fontSize:9,color:C.TE,align:"center",valign:"middle"})}
// Time saved callout
s.addShape(S.roundRect,{x:3.5,y:5.8,w:6.33,h:.85,fill:{color:"FEF3C7"},rectRadius:.12,line:{color:C.W}});
s.addText("单次节省 50 分钟  日换模 3 次  日节省 150 分钟",{x:3.5,y:5.8,w:6.33,h:.85,fontFace:"Microsoft YaHei",fontSize:13,color:C.T,bold:true,align:"center",valign:"middle"})})();

(function(){var s=pptx.addSlide();setBg(s);addTopBar(s,C.TE);addTitleBand(s,"SMED 实施效果","Results & Key Success Factors");addFooter(s,"05 | 防错与SMED详解 | SMED 实施效果");sectLabel(s,"效果数据 · 关键成果");
statCard(s,.6,1.85,"60","min → <10min","换模时间压缩",C.G);
statCard(s,3.7,1.85,"83","%","时间节省率",C.TE);
statCard(s,6.8,1.85,"3","次/日","换模频次提升",C.P);
statCard(s,9.9,1.85,"150","min/日","日节省工时",C.W);
var tx2=.5;
s.addShape(S.rect,{x:tx2,y:3.2,w:12.33,h:.44,fill:{color:C.P},line:{color:C.P}});
s.addText("指标",{x:tx2,y:3.2,w:2.4,h:.44,fontFace:"Microsoft YaHei",fontSize:11,color:C.A,bold:true,align:"center",valign:"middle"});
s.addText("改善前",{x:tx2+2.4,y:3.2,w:2.8,h:.44,fontFace:"Microsoft YaHei",fontSize:11,color:C.A,bold:true,align:"center",valign:"middle"});
s.addText("改善后",{x:tx2+5.2,y:3.2,w:2.8,h:.44,fontFace:"Microsoft YaHei",fontSize:11,color:C.A,bold:true,align:"center",valign:"middle"});
s.addText("改善幅度",{x:tx2+8.0,y:3.2,w:2.4,h:.44,fontFace:"Microsoft YaHei",fontSize:11,color:C.A,bold:true,align:"center",valign:"middle"});
var rR2=[["换模时间","60 min","< 10 min","↓ 83%"],["换模频次","1 次/日","3 次/日","↑ 200%"],["OEE 设备效率","65%","85%","↑ 20pp"],["在品库存","5000 件","1500 件","↓ 70%"],["切换损失工时","60 min/次","< 10 min/次","↓ 83%"]];
for(var i=0;i<rR2.length;i++){var ry2=3.64+i*.44;
s.addShape(S.rect,{x:tx2,y:ry2,w:12.33,h:.42,fill:{color:i%2===0?C.A:"F8FAFC"},line:{color:"CBD5E1"}});
s.addText(rR2[i][0],{x:tx2+.05,y:ry2,w:2.3,h:.42,fontFace:"Microsoft YaHei",fontSize:10,color:C.T,align:"center",valign:"middle"});
s.addText(rR2[i][1],{x:tx2+2.4,y:ry2,w:2.7,h:.42,fontFace:"Microsoft YaHei",fontSize:10,color:C.D,align:"center",valign:"middle"});
s.addText(rR2[i][2],{x:tx2+5.2,y:ry2,w:2.7,h:.42,fontFace:"Microsoft YaHei",fontSize:10,color:C.G,align:"center",valign:"middle"});
s.addText(rR2[i][3],{x:tx2+8.05,y:ry2,w:2.3,h:.42,fontFace:"Arial",fontSize:11,color:C.G,bold:true,align:"center",valign:"middle"})}
s.addText("成功关键因素",{x:.5,y:5.9,w:3.5,h:.35,fontFace:"Microsoft YaHei",fontSize:12,color:C.P,bold:true,valign:"middle"});
var sf=[{t:"标准化作业：制定换模标准流程（SOP），每个动作精确到秒",c:C.G},{t:"并行作业：多人同时操作，消除等待时间",c:C.TE},{t:"专用工具：开发快速夹紧/定位专用工装夹具",c:C.P},{t:"参数预存：模具参数数字化管理，一键调用",c:C.W}];
for(var i=0;i<sf.length;i++){var sx2=.5+i*3.15;
s.addShape(S.roundRect,{x:sx2,y:6.2,w:2.9,h:.42,fill:{color:sf[i].c},rectRadius:.08,line:{color:sf[i].c}});
s.addText(sf[i].t,{x:sx2,y:6.2,w:2.9,h:.42,fontFace:"Microsoft YaHei",fontSize:7.5,color:C.A,align:"center",valign:"middle"})}
})();

(function(){var s=pptx.addSlide();setBg(s);addTopBar(s,C.P);addTitleBand(s,"总结与行动计划","Summary & Next Steps");addFooter(s,"05 | 防错与SMED详解 | 总结");sectLabel(s,"回顾 · 行动 · 展望");
cardB(s,.5,1.78,5.9,2.4,C.G,[{t:"防错 Poka-Yoke 核心要点",y:.08,size:13,bold:true,color:C.P},{t:"1. 预防优于检测——目标是从根源消除错误",y:.45,size:10,color:C.T},{t:"2. 零成本优先——先用最简单方法解决问题",y:.75,size:10,color:C.T},{t:"3. 操作员参与——一线员工最了解现场问题",y:1.05,size:10,color:C.T},{t:"4. 持续迭代——从检测到预防的不断提升",y:1.35,size:10,color:C.T},{t:"四类型：接触法 / 定值法 / 动作步骤法 / 成组法",y:1.9,size:10,bold:true,color:C.G}]);
cardB(s,6.9,1.78,5.93,2.4,C.TE,[{t:"SMED 核心要点",y:.08,size:13,bold:true,color:C.P},{t:"1. 区分内外部——明确哪些必须停机操作",y:.45,size:10,color:C.T},{t:"2. 转化内→外——能提前准备的绝不占用停机",y:.75,size:10,color:C.T},{t:"3. 优化剩余项——简化每一个动作到极致",y:1.05,size:10,color:C.T},{t:"4. 目标<10min——分钟级换模释放产能",y:1.35,size:10,color:C.T},{t:"效果：换模时间↓83%  OEE↑20pp  库存↓70%",y:1.9,size:10,bold:true,color:C.TE}]);
s.addText("行动计划建议",{x:.5,y:4.45,w:4.0,h:.35,fontFace:"Microsoft YaHei",fontSize:12,color:C.P,bold:true,valign:"middle"});
var actions=[{t:"第1周\\n缺陷数据收集",c:C.P,w:2.5},{t:"第2周\\n5Why根因分析",c:C.G,w:2.4},{t:"第3周\\n零成本防错方案",c:C.TE,w:2.2},{t:"第4周\\n装置制作验证",c:C.W,w:2.2},{t:"第8周\\n标准化与推广",c:C.D,w:2.4}];
var ax2=.5;
for(var i=0;i<actions.length;i++){var a=actions[i];
s.addShape(S.roundRect,{x:ax2,y:4.85,w:a.w,h:.85,fill:{color:a.c},rectRadius:.1,line:{color:a.c}});
s.addText(a.t,{x:ax2,y:4.85,w:a.w,h:.85,fontFace:"Microsoft YaHei",fontSize:9,color:C.A,bold:true,align:"center",valign:"middle"});
if(i<actions.length-1){s.addShape(S.rightArrow,{x:ax2+a.w+.03,y:5.15,w:.24,h:.24,fill:{color:C.TL},line:{color:C.TL}});ax2+=a.w+.27}}
s.addShape(S.rect,{x:1,y:6.1,w:11.33,h:.55,fill:{color:"EEF2FF"},line:{color:"000000"}});
s.addText('"质量是制造出来的，不是检验出来的"  —— 防错让人不犯错；SMED让机器不停歇"',{x:1,y:6.1,w:11.33,h:.55,fontFace:"Microsoft YaHei",fontSize:13,color:C.P,bold:true,align:"center",valign:"middle"})})();

pptx.writeFile({ fileName: path.join(OUT, "05-防错与SMED详解.pptx") })
  .then(function() { console.log("OK: 05-防错与SMED详解.pptx created"); })
  .catch(function(err) { console.error("ERR:", err); process.exit(1); });

