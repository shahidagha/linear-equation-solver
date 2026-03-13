/**
 * Draws the graphical solution (two lines, points, intersection) onto a 2D canvas context.
 * Math coordinates: x, y in [-8, 8]. Canvas is scaled to fit with margins.
 */

/** Matches SolverResponse['graph'] from the API. */
export interface GraphData {
  equation1_points: Array<[string | number, string | number]>;
  equation2_points: Array<[string | number, string | number]>;
  equation1_label?: string;
  equation2_label?: string;
  intersection: Record<string, string | number>;
}

const RANGE = 8; // -8 to 8
const MARGIN = 40;
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

  // Grid: darker (black/dark gray)
  ctx.strokeStyle = '#333333';
  ctx.lineWidth = 0.5;
  ctx.beginPath();
  for (let i = -RANGE; i <= RANGE; i++) {
    const v = toCanvas(i, 0, width, height);
    ctx.moveTo(v.cx, MARGIN);
    ctx.lineTo(v.cx, height - MARGIN);
    ctx.moveTo(MARGIN, v.cy);
    ctx.lineTo(width - MARGIN, v.cy);
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
  drawArrow(ctx, left.cx, left.cy, 0);
  drawArrow(ctx, right.cx, right.cy, Math.PI);
  drawArrow(ctx, bottom.cx, bottom.cy, Math.PI / 2);
  drawArrow(ctx, top.cx, top.cy, -Math.PI / 2);

  ctx.fillStyle = BLACK;
  ctx.font = '14px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('X', right.cx + 18, right.cy + 4);
  ctx.fillText('Y', top.cx - 4, top.cy - 12);

  // Equation line 1: black, arrows at both ends, label near end
  if (p1.length >= 2) {
    const line = lineThroughPoints(p1[0], p1[1]);
    const xStart = Math.max(-RANGE, line.minX);
    const xEnd = Math.min(RANGE, line.maxX);
    const yEnd = line.getY(xEnd);
    const start = toCanvas(xStart, line.getY(xStart), width, height);
    const end = toCanvas(xEnd, yEnd, width, height);
    drawArrowedSegment(ctx, start.cx, start.cy, end.cx, end.cy);
    if (label1) {
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'left';
      ctx.fillStyle = BLACK;
      ctx.fillText(label1, end.cx + 12, end.cy + (yEnd >= 0 ? -10 : 14));
    }
  }

  // Equation line 2: black, arrows at both ends, label near end
  if (p2.length >= 2) {
    const line = lineThroughPoints(p2[0], p2[1]);
    const xStart = Math.max(-RANGE, line.minX);
    const xEnd = Math.min(RANGE, line.maxX);
    const yEnd = line.getY(xEnd);
    const start = toCanvas(xStart, line.getY(xStart), width, height);
    const end = toCanvas(xEnd, yEnd, width, height);
    drawArrowedSegment(ctx, start.cx, start.cy, end.cx, end.cy);
    if (label2) {
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'left';
      ctx.fillStyle = BLACK;
      ctx.fillText(label2, end.cx + 12, end.cy + (yEnd >= 0 ? -10 : 14));
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
  ctx.font = 'bold 11px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(`(${ix}, ${iy})`, intPt.cx + 10, intPt.cy - 5);
}
