/**
 * Draws the graphical solution (two lines, points, intersection) onto a 2D canvas context.
 * Math coordinates: x, y in [-8, 8]. Canvas is scaled to fit with margins.
 */

/** Matches SolverResponse['graph'] from the API. */
export interface GraphData {
  equation1_points: Array<[string | number, string | number]>;
  equation2_points: Array<[string | number, string | number]>;
  intersection: Record<string, string | number>;
}

const RANGE = 8; // -8 to 8
const MARGIN = 40;

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

  ctx.fillStyle = '#fff';
  ctx.fillRect(0, 0, width, height);

  const graphWidth = width - 2 * MARGIN;
  const graphHeight = height - 2 * MARGIN;

  // Grid and axes
  ctx.strokeStyle = '#e5e7eb';
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

  ctx.strokeStyle = '#1f2937';
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  const ox = toCanvas(0, 0, width, height);
  const oy = toCanvas(0, 0, width, height);
  ctx.moveTo(ox.cx, MARGIN);
  ctx.lineTo(ox.cx, height - MARGIN);
  ctx.moveTo(MARGIN, oy.cy);
  ctx.lineTo(width - MARGIN, oy.cy);
  ctx.stroke();

  // Axis labels
  ctx.fillStyle = '#374151';
  ctx.font = '12px sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('x', width / 2, height - 8);
  ctx.textAlign = 'right';
  ctx.fillText('y', MARGIN - 8, MARGIN + 4);

  // Line 1 (e.g. blue)
  if (p1.length >= 2) {
    const line = lineThroughPoints(p1[0], p1[1]);
    const xStart = Math.max(-RANGE, line.minX);
    const xEnd = Math.min(RANGE, line.maxX);
    const start = toCanvas(xStart, line.getY(xStart), width, height);
    const end = toCanvas(xEnd, line.getY(xEnd), width, height);
    ctx.strokeStyle = '#2563eb';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(start.cx, start.cy);
    ctx.lineTo(end.cx, end.cy);
    ctx.stroke();
  }

  // Line 2 (e.g. green)
  if (p2.length >= 2) {
    const line = lineThroughPoints(p2[0], p2[1]);
    const xStart = Math.max(-RANGE, line.minX);
    const xEnd = Math.min(RANGE, line.maxX);
    const start = toCanvas(xStart, line.getY(xStart), width, height);
    const end = toCanvas(xEnd, line.getY(xEnd), width, height);
    ctx.strokeStyle = '#059669';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(start.cx, start.cy);
    ctx.lineTo(end.cx, end.cy);
    ctx.stroke();
  }

  // Points on line 1
  ctx.fillStyle = '#2563eb';
  p1.forEach((p) => {
    const { cx, cy } = toCanvas(p[0], p[1], width, height);
    ctx.beginPath();
    ctx.arc(cx, cy, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#1e40af';
    ctx.lineWidth = 1;
    ctx.stroke();
  });

  // Points on line 2
  ctx.fillStyle = '#059669';
  p2.forEach((p) => {
    const { cx, cy } = toCanvas(p[0], p[1], width, height);
    ctx.beginPath();
    ctx.arc(cx, cy, 5, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#047857';
    ctx.lineWidth = 1;
    ctx.stroke();
  });

  // Intersection
  const intPt = toCanvas(ix, iy, width, height);
  ctx.fillStyle = '#dc2626';
  ctx.beginPath();
  ctx.arc(intPt.cx, intPt.cy, 6, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = '#b91c1c';
  ctx.lineWidth = 2;
  ctx.stroke();
  ctx.fillStyle = '#1f2937';
  ctx.font = 'bold 11px sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(`(${ix}, ${iy})`, intPt.cx + 10, intPt.cy - 5);
}
