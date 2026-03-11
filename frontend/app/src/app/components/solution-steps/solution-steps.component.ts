import { AfterViewChecked, Component, ElementRef, Input, QueryList, ViewChildren } from '@angular/core';
import { CommonModule } from '@angular/common';
import katex from 'katex';
import { SolverResponse, SolverStep } from '../../models/solver-response.model';
import { VerbosityLevel } from '../../services/solver-state.service';

@Component({
  selector: 'app-solution-steps',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './solution-steps.component.html',
  styleUrl: './solution-steps.component.css'
})
export class SolutionStepsComponent implements AfterViewChecked {
  @Input() methods: SolverResponse['methods'] | null = null;
  @Input() graph: SolverResponse['graph'] | null = null;
  @Input() selectedMethod = 'elimination';
  @Input() verbosity: VerbosityLevel = 'detailed';

  @ViewChildren('mathBlock') mathBlocks!: QueryList<ElementRef<HTMLDivElement>>;

  get eliminationSteps(): SolverStep[] {
    const steps = this.methods?.elimination ?? [];
    if (this.verbosity === 'short') {
      return steps.length > 1 ? [steps[0], steps[steps.length - 1]] : steps;
    }
    if (this.verbosity === 'medium') {
      return steps.filter((_, index) => index % 2 === 0 || index === steps.length - 1);
    }
    return steps;
  }

  get graphicalSteps(): string[] {
    return this.methods?.graphical_steps ?? [];
  }

  ngAfterViewChecked(): void {
    this.mathBlocks?.forEach((block) => {
      const content = block.nativeElement.dataset['latex'] ?? '';
      katex.render(content, block.nativeElement, { throwOnError: false, displayMode: true });
    });
  }

  toLatex(step: SolverStep): string {
    if (step.type === 'vertical_elimination') {
      return `\\begin{aligned}${step.eq1}\\\\${step.eq2}\\\\\\hline ${step.result}\\end{aligned}`;
    }
    return step.content ?? '';
  }
}
