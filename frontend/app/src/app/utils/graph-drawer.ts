/**
 * Draws the graphical solution (two lines, points, intersection) onto a 2D canvas context.
 * Graph display range: x, y in [-9, 9]. Point selection (backend) remains [-8, 8].
 */

/** Matches SolverResponse['graph'] from the API. */
export interface GraphData {
  equation1_points: Array<[string | number, string | number]>;
  equation2_points: Array<[string | number, string | number]>;
  equation1_label?: string;
  equation2_label?: string;
  intersection: Record<string, string | number>;
}

const RANGE = 9; // graph axes and grid: -9 to 9 (point selection stays -8 to 8 in backend)
const MARGIN = 28;
const BLACK = '#000000';

/** Convert LaTeX-like label to plain text for canvas (e.g. \frac{1}{2} -> 1/2). */
function latexLabelToPlain(s: string): string {
  if (!s) return '';
  return s
    .replace(/\\frac\{([^}]*)\}\{([^}]*)\}/g, '($1)/($2)')
    .replace(/\\sqrt\{([^}]*)\}/g, '√($1)')
    .replace(/\\/g, '')
    .trim();
}

/** Draw an arrow at (cx, cy) in the direction of angle (radians). */
function drawArrow(ctx: CanvasRenderingContext2D, cx: number, cy: number, angle: number, size = 8): void {
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(angle);
  ctx.beginPath();
  ctx.moveTo(size, 0);
  ctx.lineTo(-size * 0.6, size * 0.5);
  ctx.lineTo(-size * 0.6, -size * 0.5);
  ctx.closePath();
  ctx.fillStyle = BLACK;
  ctx.fill();
  ctx.strokeStyle = BLACK;
  ctx.lineWidth = 1;
  ctx.stroke();
  ctx.restore();
}

/** Draw a line segment with arrows at both ends. */
function drawArrowedSegment(
  ctx: CanvasRenderingContext2D,
  x1: number, y1: number, x2: number, y2: number
): void {
  ctx.strokeStyle = BLACK;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.stroke();
  const dx = x2 - x1;
  const dy = y2 - y1;
  const len = Math.hypot(dx, dy) || 1;
  const ux = dx / len;
  const uy = dy / len;
  drawArrow(ctx, x1, y1, Math.atan2(-uy, -ux));
  drawArrow(ctx, x2, y2, Math.atan2(uy, ux));
}

/** Draw text along a line near the visible end (arrow): t near 1 = near end, side = ±1 for opposite sides. */
function drawLabelAlongLine(
  ctx: CanvasRenderingContext2D,
  startCx: number, startCy: number, endCx: number, endCy: number,
  label: string,
  t = 0.82,
  side: 1 | -1 = 1
): void {
  const dx = endCx - startCx;
  const dy = endCy - startCy;
  const len = Math.hypot(dx, dy) || 1;
  const px = startCx + t * dx;
  const py = startCy + t * dy;
  const offset = 12;
  const nx = -dy / len;
  const ny = dx / len;
  const tx = px + side * offset * nx;
  const ty = py + side * offset * ny;
  const angle = Math.atan2(dy, dx);
  ctx.save();
  ctx.translate(tx, ty);
  ctx.rotate(angle);
  ctx.font = 'bold 13px sans-serif';
  ctx.fillStyle = BLACK;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(label, 0, 0);
  ctx.restore();
}

function toNum(v: number | string): number {
  const n = typeof v === 'number' ? v : parseFloat(String(v));
  return Number.isFinite(n) ? n : 0;
}

function lineThroughPoints(
  p1: [number, number],
  p2: [number, number]
): { minX: number; maxX: number; getY: (x: number) => number } {
  const [x1, y1] = p1;
  const [x2, y2] = p2;
  const dx = x2 - x1;
  if (Math.abs(dx) < 1e-9) {
    return {
      minX: x1,
      maxX: x1,
      getY: () => (y1 + y2) / 2,
    };
  }
  const slope = (y2 - y1) / dx;
  const getY = (x: number) => y1 + slope * (x - x1);
  return { minX: -RANGE, maxX: RANGE, getY };
}

/** Clip line to box [-RANGE,RANGE] x [-RANGE,RANGE]; return the two boundary points. */
function clipLineToBox(
  p1: [number, number],
  p2: [number, number]
): [[number, number], [number, number]] {
  const [x1, y1] = p1;
  const [x2, y2] = p2;
  const dx = x2 - x1;
  const pts: [number, number][] = [];

  if (Math.abs(dx) < 1e-9) {
    const x = Math.max(-RANGE, Math.min(RANGE, x1));
    return [[x, -RANGE], [x, RANGE]];
  }

  const slope = (y2 - y1) / dx;
  const getY = (x: number) => y1 + slope * (x - x1);
  const getX = (y: number) => x1 + (y - y1) / slope;

  const yAtLeft = getY(-RANGE);
  if (yAtLeft >= -RANGE && yAtLeft <= RANGE) pts.push([-RANGE, yAtLeft]);
  const yAtRight = getY(RANGE);
  if (yAtRight >= -RANGE && yAtRight <= RANGE) pts.push([RANGE, yAtRight]);
  const xAtBottom = getX(-RANGE);
  if (xAtBottom >= -RANGE && xAtBottom <= RANGE) pts.push([xAtBottom, -RANGE]);
  const xAtTop = getX(RANGE);
  if (xAtTop >= -RANGE && xAtTop <= RANGE) pts.push([xAtTop, RANGE]);

  const uniq = (arr: [number, number][]) => {
    const seen = new Set<string>();
    return arr.filter((p) => {
      const k = `${p[0].toFixed(4)}_${p[1].toFixed(4)}`;
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    });
  };
  const two = uniq(pts);
  if (two.length < 2) return [[p1[0], p1[1]], [p2[0], p2[1]]];
  two.sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  return [two[0], two[two.length - 1]];
}

function toCanvas(
  x: number,
  y: number,
  width: number,
  height: number
): { cx: number; cy: number } {
  const graphWidth = width - 2 * MARGIN;
  const graphHeight = height - 2 * MARGIN;
  const cx = MARGIN + ((x + RANGE) / (2 * RANGE)) * graphWidth;
  const cy = MARGIN + ((RANGE - y) / (2 * RANGE)) * graphHeight;
  return { cx, cy };
}

export function drawGraph(
  ctx: CanvasRenderingContext2D,
  graphData: GraphData,
  width: number,
  height: number
): void {
  const p1 = (graphData.equation1_points || []).map((p) => [toNum(p[0]), toNum(p[1])] as [number, number]);
  const p2 = (graphData.equation2_points || []).map((p) => [toNum(p[0]), toNum(p[1])] as [number, number]);
  const inter = graphData.intersection || {};
  const vals = Object.values(inter).map(toNum);
  const ix = vals[0] ?? 0;
  const iy = vals[1] ?? 0;
  const label1 = latexLabelToPlain(graphData.equation1_label || '');
  const label2 = latexLabelToPlain(graphData.equation2_label || '');

  ctx.fillStyle = '#fff';
  ctx.fillRect(0, 0, width, height);

  const graphWidth = width - 2 * MARGIN;
  const graphHeight = height - 2 * MARGIN;

  // Grid: black – vertical and horizontal lines
  ctx.strokeStyle = BLACK;
  ctx.lineWidth = 0.5;
  ctx.beginPath();
  for (let i = -RANGE; i <= RANGE; i++) {
    const vert = toCanvas(i, 0, width, height);
    ctx.moveTo(vert.cx, MARGIN);
    ctx.lineTo(vert.cx, height - MARGIN);
    const horz = toCanvas(0, i, width, height);
    ctx.moveTo(MARGIN, horz.cy);
    ctx.lineTo(width - MARGIN, horz.cy);
  }
  ctx.stroke();

  // Axes with arrows at both ends, labeled X and Y
  const left = toCanvas(-RANGE, 0, width, height);
  const right = toCanvas(RANGE, 0, width, height);
  const bottom = toCanvas(0, -RANGE, width, height);
  const top = toCanvas(0, RANGE, width, height);
  ctx.strokeStyle = BLACK;
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  ctx.moveTo(left.cx, left.cy);
  ctx.lineTo(right.cx, right.cy);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(bottom.cx, bottom.cy);
  ctx.lineTo(top.cx, top.cy);
  ctx.stroke();
  drawArrow(ctx, left.cx, left.cy, Math.PI);
  drawArrow(ctx, right.cx, right.cy, 0);
  drawArrow(ctx, bottom.cx, bottom.cy, Math.PI / 2);
  drawArrow(ctx, top.cx, top.cy, -Math.PI / 2);

  ctx.fillStyle = BLACK;
  ctx.font = '14px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('X', right.cx + 18, right.cy + 4);
  ctx.fillText('Y', top.cx - 4, top.cy - 12);

  // Axis tick labels: -RANGE to RANGE on X and Y (single 0 at origin)
  const origin = toCanvas(0, 0, width, height);
  ctx.font = '11px sans-serif';
  ctx.fillStyle = BLACK;
  const labelOffset = 3;
  for (let i = -RANGE; i <= RANGE; i++) {
    const v = toCanvas(i, 0, width, height);
    ctx.textAlign = i === 0 ? 'left' : 'center';
    ctx.fillText(String(i), v.cx + labelOffset, origin.cy + 16);
    if (i === 0) continue;
    const h = toCanvas(0, i, width, height);
    ctx.textAlign = 'right';
    ctx.fillText(String(i), origin.cx - 6, h.cy + 4 + labelOffset);
  }

  // Equation line 1: clip to graph box so both end arrows are visible
  if (p1.length >= 2) {
    const [b1, b2] = clipLineToBox(p1[0], p1[1]);
    const start = toCanvas(b1[0], b1[1], width, height);
    const end = toCanvas(b2[0], b2[1], width, height);
    drawArrowedSegment(ctx, start.cx, start.cy, end.cx, end.cy);
    if (label1) {
      drawLabelAlongLine(ctx, start.cx, start.cy, end.cx, end.cy, label1, 0.82, 1);
    }
  }

  // Equation line 2: clip to graph box so both end arrows are visible
  if (p2.length >= 2) {
    const [b1, b2] = clipLineToBox(p2[0], p2[1]);
    const start = toCanvas(b1[0], b1[1], width, height);
    const end = toCanvas(b2[0], b2[1], width, height);
    drawArrowedSegment(ctx, start.cx, start.cy, end.cx, end.cy);
    if (label2) {
      drawLabelAlongLine(ctx, start.cx, start.cy, end.cx, end.cy, label2, 0.82, -1);
    }
  }

  // Points on line 1 – black
  ctx.fillStyle = BLACK;
  ctx.strokeStyle = BLACK;
  ctx.lineWidth = 1;
  p1.forEach((p) => {
    const { cx, cy } = toCanvas(p[0], p[1], width, height);
    ctx.beginPath();
    ctx.arc(cx, cy, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  });

  // Points on line 2 – black
  p2.forEach((p) => {
    const { cx, cy } = toCanvas(p[0], p[1], width, height);
    ctx.beginPath();
    ctx.arc(cx, cy, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  });

  // Intersection – black
  const intPt = toCanvas(ix, iy, width, height);
  ctx.beginPath();
  ctx.arc(intPt.cx, intPt.cy, 6, 0, Math.PI * 2);
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.font = 'bold 15px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(`(${ix}, ${iy})`, intPt.cx + 12, intPt.cy - 5);
}
