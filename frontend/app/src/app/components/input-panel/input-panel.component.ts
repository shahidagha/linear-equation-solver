import { Component } from '@angular/core';
import { VariableSelectorComponent } from '../variable-selector/variable-selector.component';
import { EquationBuilderComponent } from '../equation-builder/equation-builder.component';

@Component({
  selector: 'app-input-panel',
  standalone: true,
  imports: [VariableSelectorComponent, EquationBuilderComponent],
  templateUrl: './input-panel.component.html',
  styleUrl: './input-panel.component.css'
})
export class InputPanelComponent {

  variable1 = 'x';
  variable2 = 'y';

  onVariable1Change(variable: string): void {
    this.variable1 = variable || 'x';
  }

  onVariable2Change(variable: string): void {
    this.variable2 = variable || 'y';
  }

}
