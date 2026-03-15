import { Component, ChangeDetectorRef } from '@angular/core';
import { AsyncPipe, KeyValuePipe, NgFor, NgIf, TitleCasePipe } from '@angular/common';
import { combineLatest, take } from 'rxjs';
import * as katex from 'katex';
import { saveAs } from 'file-saver';
import {
  Document,
  Packer,
  Paragraph,
  ImageRun,
  AlignmentType,
} from 'docx';
import html2canvas from 'html2canvas';
import html2pdf from 'html2pdf.js';
import { MethodSelectorComponent } from '../method-selector/method-selector.component';
import { SolutionStepsComponent } from '../solution-steps/solution-steps.component';
import { ViewGraphModalComponent } from '../view-graph-modal/view-graph-modal.component';
import { SolverStateService, VerbosityLevel } from '../../services/solver-state.service';
import { equationToLatex } from '../../utils/latex-generator';
import { MethodLatexPayload, SolverResponse } from '../../models/solver-response.model';
import { drawGraph } from '../../utils/graph-drawer';

@Component({
  selector: 'app-solution-panel',
  standalone: true,
  imports: [NgIf, NgFor, AsyncPipe, KeyValuePipe, TitleCasePipe, MethodSelectorComponent, SolutionStepsComponent, ViewGraphModalComponent],
  templateUrl: './solution-panel.component.html',
  styleUrl: './solution-panel.component.css'
})
export class SolutionPanelComponent {
  readonly verbosities: VerbosityLevel[] = ['detailed', 'medium', 'short'];

  /** Shown after Copy Solution or Copy graph: 'success' | 'failure' | null. Cleared after a short delay. */
  copySolutionMessage: 'success' | 'failure' | null = null;
  private copySolutionTimeout: ReturnType<typeof setTimeout> | null = null;

  graphModalOpen = false;

  constructor(
    public readonly state: SolverStateService,
    private readonly cdr: ChangeDetectorRef
  ) {}

  onMethodSelected(method: string): void { this.state.setSelectedMethod(method); }
  setVerbosity(level: VerbosityLevel): void { this.state.setVerbosity(level); }
  exitSolution(): void { this.state.resetSolutionState(); }

  /** Display names for Copy Question instruction line. */
  private static readonly METHOD_DISPLAY_NAMES: Record<string, string> = {
    elimination: 'Elimination method',
    substitution: 'Substitution method',
    cramer: "Cramer's rule",
    graphical: 'Graphical method',
  };

  /** Escape a string for use inside LaTeX \text{...}. */
  private static escapeForLatexText(s: string): string {
    return s.replace(/\\/g, '\\textbackslash{}').replace(/[{}]/g, (c) => (c === '{' ? '\\{' : '\\}'));
  }

  copyQuestion(): void {
    this.clearCopySolutionMessage();
    combineLatest([
      this.state.equations$,
      this.state.variables$,
      this.state.selectedMethod$,
    ]).pipe(take(1)).subscribe(([eqs, vars, selectedMethod]) => {
      if (!eqs?.equation1 || !eqs?.equation2) {
        this.showCopySolutionMessage('failure');
        return;
      }
      const latex1 = equationToLatex(eqs.equation1 as any, vars as any);
      const latex2 = equationToLatex(eqs.equation2 as any, vars as any);
      const methodName = SolutionPanelComponent.METHOD_DISPLAY_NAMES[selectedMethod || 'elimination']
        ?? 'Elimination method';
      const instructionText = SolutionPanelComponent.escapeForLatexText(
        `Solve the following simultaneous equations by ${methodName}.`
      );
      const rawLatex = `\\begin{aligned}\n&\\text{${instructionText}} \\\\\n&${latex1} \\; ; \\; ${latex2}\n\\end{aligned}`;
      navigator.clipboard.writeText(rawLatex)
        .then(() => this.showCopySolutionMessage('success'))
        .catch(() => this.showCopySolutionMessage('failure'));
    });
  }

  copySolution(): void {
    this.clearCopySolutionMessage();
    combineLatest([
      this.state.methods$,
      this.state.selectedMethod$,
      this.state.verbosity$
    ]).pipe(take(1)).subscribe(([methods, selectedMethod, verbosity]) => {
      const methodKey = `${selectedMethod || 'elimination'}_latex`;
      const payload = methods?.[methodKey] as MethodLatexPayload | undefined;
      const verbosityKey = `latex_${verbosity || 'detailed'}` as keyof MethodLatexPayload;
      const rawLatex = payload?.[verbosityKey];

      if (typeof rawLatex !== 'string' || !rawLatex.trim()) {
        this.showCopySolutionMessage('failure');
        return;
      }

      navigator.clipboard.writeText(rawLatex.trim())
        .then(() => this.showCopySolutionMessage('success'))
        .catch(() => this.showCopySolutionMessage('failure'));
    });
  }

  private showCopySolutionMessage(status: 'success' | 'failure'): void {
    this.copySolutionMessage = status;
    this.cdr.detectChanges();
    this.copySolutionTimeout = setTimeout(() => {
      this.copySolutionMessage = null;
      this.copySolutionTimeout = null;
      this.cdr.detectChanges();
    }, 2500);
  }

  private clearCopySolutionMessage(): void {
    if (this.copySolutionTimeout != null) {
      clearTimeout(this.copySolutionTimeout);
      this.copySolutionTimeout = null;
    }
    this.copySolutionMessage = null;
  }

  openGraphModal(): void {
    this.graphModalOpen = true;
  }

  closeGraphModal(): void {
    this.graphModalOpen = false;
  }

  copyGraphAsPng(): void {
    this.clearCopySolutionMessage();
    this.state.graph$.pipe(take(1)).subscribe((graph) => {
      if (!graph?.equation1_points?.length || !graph?.equation2_points?.length) {
        this.showCopySolutionMessage('failure');
        return;
      }
      const canvas = document.createElement('canvas');
      const size = 560;
      canvas.width = size;
      canvas.height = size;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        this.showCopySolutionMessage('failure');
        return;
      }
      drawGraph(ctx, graph as any, size, size);
      canvas.toBlob(
        (blob) => {
          if (!blob) {
            this.showCopySolutionMessage('failure');
            return;
          }
          navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })])
            .then(() => this.showCopySolutionMessage('success'))
            .catch(() => this.showCopySolutionMessage('failure'));
        },
        'image/png',
        1
      );
    });
  }

  /** Build question LaTeX (instruction + equations) and solution LaTeX for the current method/verbosity. */
  private getExportContent(
    eqs: { equation1?: unknown; equation2?: unknown } | null,
    vars: { var1: string; var2: string } | null,
    methods: SolverResponse['methods'] | null,
    selectedMethod: string,
    verbosity: VerbosityLevel
  ): { questionLatex: string; solutionLatex: string } | null {
    if (!eqs?.equation1 || !eqs?.equation2 || !vars?.var1 || !vars?.var2) return null;
    const latex1 = equationToLatex(eqs.equation1 as any, vars);
    const latex2 = equationToLatex(eqs.equation2 as any, vars);
    const methodName = SolutionPanelComponent.METHOD_DISPLAY_NAMES[selectedMethod] ?? 'Elimination method';
    const instructionText = SolutionPanelComponent.escapeForLatexText(
      `Solve the following simultaneous equations by ${methodName}.`
    );
    const questionLatex = `\\begin{aligned}\n&\\text{${instructionText}} \\\\\n&${latex1} \\; ; \\; ${latex2}\n\\end{aligned}`;

    const methodKey = `${selectedMethod}_latex`;
    const methodsMap = methods as Record<string, MethodLatexPayload> | null;
    const payload = methodsMap?.[methodKey];
    const verbosityKey = `latex_${verbosity}` as keyof MethodLatexPayload;
    const solutionLatex = (payload?.[verbosityKey] as string)?.trim?.();
    if (typeof solutionLatex !== 'string' || !solutionLatex) return null;

    return { questionLatex, solutionLatex };
  }

  /** Render LaTeX string to HTML using KaTeX (display mode). */
  private latexToHtml(latex: string): string {
    try {
      return katex.renderToString(latex, { displayMode: true, throwOnError: false });
    } catch {
      return `<span class="katex-error">${escapeHtml(latex)}</span>`;
    }
  }

  /** Draw graph to a canvas (same as copy graph); returns data URL or null if no graph. */
  private getGraphImageDataUrl(graph: SolverResponse['graph'] | null): string | null {
    if (!graph?.equation1_points?.length || !graph?.equation2_points?.length) return null;
    const canvas = document.createElement('canvas');
    const size = 560;
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;
    drawGraph(ctx, graph as any, size, size);
    return canvas.toDataURL('image/png');
  }

  exportToPdf(): void {
    this.clearCopySolutionMessage();
    combineLatest([
      this.state.equations$,
      this.state.variables$,
      this.state.methods$,
      this.state.graph$,
      this.state.selectedMethod$,
      this.state.verbosity$,
    ])
      .pipe(take(1))
      .subscribe(([eqs, vars, methods, graph, selectedMethod, verbosity]) => {
        const content = this.getExportContent(
          eqs ?? null,
          vars && typeof vars === 'object' && 'var1' in vars ? vars : null,
          methods ?? null,
          selectedMethod || 'elimination',
          verbosity || 'detailed'
        );
        if (!content) {
          this.showCopySolutionMessage('failure');
          return;
        }
        const questionHtml = this.latexToHtml(content.questionLatex);
        const solutionHtml = this.latexToHtml(content.solutionLatex);
        const isGraphical = selectedMethod === 'graphical';
        const graphDataUrl = isGraphical ? this.getGraphImageDataUrl(graph ?? null) : null;
        const graphSection = graphDataUrl
          ? `<div style="page-break-inside: avoid;"><h2 style="margin:24px 0 16px;">Graph</h2><div class="export-block"><img src="${graphDataUrl}" alt="Graph of the two lines" style="max-width:100%; max-height:420px; width:auto; height:auto; display:block;" /></div></div>`
          : '';
        const wrapper = document.createElement('div');
        wrapper.className = 'export-pdf-wrapper';
        wrapper.style.cssText = 'padding:24px; font-family:serif; max-width:800px;';
        wrapper.innerHTML = `
          <h2 style="margin-bottom:16px;">Question</h2>
          <div class="katex export-block">${questionHtml}</div>
          <h2 style="margin:24px 0 16px;">Solution</h2>
          <div class="katex export-block">${solutionHtml}</div>
          ${graphSection}
        `;
        document.body.appendChild(wrapper);
        const opts = { margin: 10, image: { type: 'jpeg' as const, quality: 0.98 } };
        html2pdf()
          .set(opts)
          .from(wrapper)
          .save('export.pdf')
          .then(() => {
            document.body.removeChild(wrapper);
            this.showCopySolutionMessage('success');
          })
          .catch(() => {
            if (wrapper.parentNode) document.body.removeChild(wrapper);
            this.showCopySolutionMessage('failure');
          });
      });
  }

  exportToWord(): void {
    this.clearCopySolutionMessage();
    combineLatest([
      this.state.equations$,
      this.state.variables$,
      this.state.methods$,
      this.state.graph$,
      this.state.selectedMethod$,
      this.state.verbosity$,
    ])
      .pipe(take(1))
      .subscribe(async ([eqs, vars, methods, graph, selectedMethod, verbosity]) => {
        const content = this.getExportContent(
          eqs ?? null,
          vars && typeof vars === 'object' && 'var1' in vars ? vars : null,
          methods ?? null,
          selectedMethod || 'elimination',
          verbosity || 'detailed'
        );
        if (!content) {
          this.showCopySolutionMessage('failure');
          return;
        }
        const questionHtml = this.latexToHtml(content.questionLatex);
        const solutionHtml = this.latexToHtml(content.solutionLatex);
        const maxWidth = 450;
        const container = document.createElement('div');
        container.style.cssText = 'position:absolute; left:-9999px; top:0; padding:20px; max-width:' + maxWidth + 'px; background:#fff;';
        container.innerHTML = `
          <div class="katex export-q">${questionHtml}</div>
          <div class="katex export-s" style="margin-top:20px;">${solutionHtml}</div>
        `;
        document.body.appendChild(container);
        try {
          const [qEl, sEl] = [container.querySelector('.export-q'), container.querySelector('.export-s')] as [HTMLElement, HTMLElement];
          if (!qEl || !sEl) throw new Error('Elements not found');
          const [canvasQ, canvasS] = await Promise.all([
            html2canvas(qEl, { scale: 2, useCORS: true, logging: false }),
            html2canvas(sEl, { scale: 2, useCORS: true, logging: false }),
          ]);
          document.body.removeChild(container);
          const toArrayBuffer = (c: HTMLCanvasElement): Promise<ArrayBuffer> =>
            new Promise((res, rej) => {
              c.toBlob(
                (b) => (b ? b.arrayBuffer().then(res) : rej(new Error('blob failed'))),
                'image/png',
                1
              );
            });
          const [bufQ, bufS] = await Promise.all([toArrayBuffer(canvasQ), toArrayBuffer(canvasS)]);
          const scaleImg = (w: number, h: number) => {
            if (w <= maxWidth) return { width: Math.round(w), height: Math.round(h) };
            const r = maxWidth / w;
            return { width: maxWidth, height: Math.round(h * r) };
          };
          const children: Paragraph[] = [
            new Paragraph({ text: 'Question', heading: 'Heading1', alignment: AlignmentType.LEFT }),
            new Paragraph({
              children: [
                new ImageRun({
                  data: new Uint8Array(bufQ),
                  type: 'png',
                  transformation: scaleImg(canvasQ.width, canvasQ.height),
                }),
              ],
            }),
            new Paragraph({ text: 'Solution', heading: 'Heading1', alignment: AlignmentType.LEFT }),
            new Paragraph({
              children: [
                new ImageRun({
                  data: new Uint8Array(bufS),
                  type: 'png',
                  transformation: scaleImg(canvasS.width, canvasS.height),
                }),
              ],
            }),
          ];
          const isGraphical = selectedMethod === 'graphical';
          if (isGraphical && graph?.equation1_points?.length && graph?.equation2_points?.length) {
            const graphCanvas = document.createElement('canvas');
            const size = 560;
            graphCanvas.width = size;
            graphCanvas.height = size;
            const ctx = graphCanvas.getContext('2d');
            if (ctx) {
              drawGraph(ctx, graph as any, size, size);
              const bufGraph = await toArrayBuffer(graphCanvas);
              children.push(
                new Paragraph({ text: 'Graph', heading: 'Heading1', alignment: AlignmentType.LEFT }),
                new Paragraph({
                  children: [
                    new ImageRun({
                      data: new Uint8Array(bufGraph),
                      type: 'png',
                      transformation: scaleImg(graphCanvas.width, graphCanvas.height),
                    }),
                  ],
                })
              );
            }
          }
          const doc = new Document({
            sections: [{ children }],
          });
          const blob = await Packer.toBlob(doc);
          saveAs(blob, 'export.docx');
          this.showCopySolutionMessage('success');
        } catch {
          if (container.parentNode) document.body.removeChild(container);
          this.showCopySolutionMessage('failure');
        }
      });
  }
}

function escapeHtml(s: string): string {
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}
