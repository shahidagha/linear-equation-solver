import { AfterViewChecked, Component, ElementRef, Input, QueryList, ViewChildren } from '@angular/core';
import { CommonModule } from '@angular/common';
import katex from 'katex';
import { SolverResponse } from '../../models/solver-response.model';
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

  get selectedLatex(): string | null {
    const methodKey = `${this.selectedMethod}_latex`;
    const methodPayload = this.methods?.[methodKey] as SolverResponse['methods']['elimination_latex'] | undefined;

    if (!methodPayload) {
      return null;
    }

    const verbosityKey = `latex_${this.verbosity}` as keyof typeof methodPayload;

    return methodPayload[verbosityKey] ?? null;
  }

  ngAfterViewChecked(): void {
    this.mathBlocks?.forEach((block) => {
      const content = block.nativeElement.dataset['latex'] ?? '';
      katex.render(content, block.nativeElement, { throwOnError: false, displayMode: true });
    });
  }
}
