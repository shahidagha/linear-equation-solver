import { Component } from '@angular/core';
import { InputPanelComponent } from '../../components/input-panel/input-panel.component';
import { RightPanelComponent } from '../../components/right-panel/right-panel.component';
import { SolverResponse } from '../../models/solver-response.model';
import { SolverStateService } from '../../services/solver-state.service';

@Component({
  selector: 'app-solver-page',
  standalone: true,
  imports: [InputPanelComponent, RightPanelComponent],
  templateUrl: './solver-page.component.html',
  styleUrl: './solver-page.component.css'
})
export class SolverPageComponent {
  constructor(private readonly state: SolverStateService) {}

  onSolved(response: SolverResponse): void {
    this.state.setResponse(null, response);
  }
}
