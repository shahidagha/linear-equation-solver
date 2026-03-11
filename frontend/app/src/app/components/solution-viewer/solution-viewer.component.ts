import { Component, Input } from '@angular/core';
import { CommonModule, KeyValue } from '@angular/common';
import { MethodSelectorComponent } from '../method-selector/method-selector.component';
import { SolutionStepsComponent } from '../solution-steps/solution-steps.component';
import { SavedSystemsComponent } from '../saved-systems/saved-systems.component';
import { SolverResponse } from '../../models/solver-response.model';

@Component({
  selector: 'app-solution-viewer',
  standalone: true,
  imports: [CommonModule, MethodSelectorComponent, SolutionStepsComponent, SavedSystemsComponent],
  templateUrl: './solution-viewer.component.html',
  styleUrl: './solution-viewer.component.css'
})
export class SolutionViewerComponent {
  @Input() response: SolverResponse | null = null;

  selectedMethod = 'elimination';

  onMethodSelected(method: string): void {
    this.selectedMethod = method;
  }

  keepOriginalOrder = (a: KeyValue<string, unknown>, b: KeyValue<string, unknown>): number => 0;
}
