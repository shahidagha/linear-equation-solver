import { Component } from '@angular/core';
import { InputPanelComponent } from '../../components/input-panel/input-panel.component';
import { SolutionViewerComponent } from '../../components/solution-viewer/solution-viewer.component';
import { SolverResponse } from '../../models/solver-response.model';

@Component({
  selector: 'app-solver-page',
  standalone: true,
  imports: [InputPanelComponent, SolutionViewerComponent],
  templateUrl: './solver-page.component.html',
  styleUrl: './solver-page.component.css'
})
export class SolverPageComponent {
  solverResponse: SolverResponse | null = null;

  onSolved(response: SolverResponse): void {
    this.solverResponse = response;
  }
}
