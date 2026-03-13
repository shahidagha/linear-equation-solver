import { Component } from '@angular/core';
import { AsyncPipe, KeyValuePipe, NgFor, NgIf, TitleCasePipe } from '@angular/common';
import { combineLatest, take } from 'rxjs';
import { MethodSelectorComponent } from '../method-selector/method-selector.component';
import { SolutionStepsComponent } from '../solution-steps/solution-steps.component';
import { SolverStateService, VerbosityLevel } from '../../services/solver-state.service';
import { equationToLatex } from '../../utils/latex-generator';

@Component({
  selector: 'app-solution-panel',
  standalone: true,
  imports: [NgIf, NgFor, AsyncPipe, KeyValuePipe, TitleCasePipe, MethodSelectorComponent, SolutionStepsComponent],
  templateUrl: './solution-panel.component.html',
  styleUrl: './solution-panel.component.css'
})
export class SolutionPanelComponent {
  readonly verbosities: VerbosityLevel[] = ['detailed', 'medium', 'short'];

  constructor(public readonly state: SolverStateService) {}

  onMethodSelected(method: string): void { this.state.setSelectedMethod(method); }
  setVerbosity(level: VerbosityLevel): void { this.state.setVerbosity(level); }
  exitSolution(): void { this.state.resetSolutionState(); }

  copyQuestion(): void {
    combineLatest([this.state.equations$, this.state.variables$]).pipe(take(1)).subscribe(([eqs, vars]) => {
      const latex1 = equationToLatex(eqs.equation1 as any, vars as any);
      const latex2 = equationToLatex(eqs.equation2 as any, vars as any);
      const rawLatex = `${latex1} ; ${latex2}`;
      navigator.clipboard.writeText(rawLatex).catch(() => {});
    });
  }

  copySolution(): void {}
}
