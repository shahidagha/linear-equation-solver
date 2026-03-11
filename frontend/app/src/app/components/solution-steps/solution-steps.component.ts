import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { SolverResponse, SolverStep } from '../../models/solver-response.model';

@Component({
  selector: 'app-solution-steps',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './solution-steps.component.html',
  styleUrl: './solution-steps.component.css'
})
export class SolutionStepsComponent {
  @Input() response: SolverResponse | null = null;
  @Input() selectedMethod = 'elimination';

  get eliminationSteps(): SolverStep[] {
    return this.response?.methods?.elimination ?? [];
  }

  get graphicalSteps(): string[] {
    return this.response?.methods?.graphical_steps ?? [];
  }
}
