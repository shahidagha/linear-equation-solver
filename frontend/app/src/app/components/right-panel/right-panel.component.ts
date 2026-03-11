import { Component } from '@angular/core';
import { AsyncPipe, NgIf } from '@angular/common';
import { SavedSystemsComponent } from '../saved-systems/saved-systems.component';
import { SolutionPanelComponent } from '../solution-panel/solution-panel.component';
import { SolverStateService } from '../../services/solver-state.service';

@Component({
  selector: 'app-right-panel',
  standalone: true,
  imports: [NgIf, AsyncPipe, SavedSystemsComponent, SolutionPanelComponent],
  templateUrl: './right-panel.component.html',
  styleUrl: './right-panel.component.css'
})
export class RightPanelComponent {
  constructor(public readonly state: SolverStateService) {}
}
