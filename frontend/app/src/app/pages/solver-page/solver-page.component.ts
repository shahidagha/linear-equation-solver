import { Component } from '@angular/core';
import { InputPanelComponent } from '../../components/input-panel/input-panel.component';

@Component({
  selector: 'app-solver-page',
  standalone: true,
  imports: [InputPanelComponent],
  templateUrl: './solver-page.component.html',
  styleUrl: './solver-page.component.css'
})
export class SolverPageComponent {

}