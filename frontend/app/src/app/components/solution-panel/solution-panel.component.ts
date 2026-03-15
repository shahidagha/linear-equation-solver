import { Component, ChangeDetectorRef } from '@angular/core';
import { AsyncPipe, KeyValuePipe, NgFor, NgIf, TitleCasePipe } from '@angular/common';
import { combineLatest, take } from 'rxjs';
import { MethodSelectorComponent } from '../method-selector/method-selector.component';
import { SolutionStepsComponent } from '../solution-steps/solution-steps.component';
import { ViewGraphModalComponent } from '../view-graph-modal/view-graph-modal.component';
import { SolverStateService, VerbosityLevel } from '../../services/solver-state.service';
import { equationToLatex } from '../../utils/latex-generator';
import { MethodLatexPayload } from '../../models/solver-response.model';
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
}
