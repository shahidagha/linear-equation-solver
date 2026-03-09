import { Component } from '@angular/core';
import { VariableSelectorComponent } from '../variable-selector/variable-selector.component';
import { EquationBuilderComponent } from '../equation-builder/equation-builder.component';
import { EquationApiService } from '../../services/equation-api.service';
@Component({
  selector: 'app-input-panel',
  standalone: true,
  imports: [VariableSelectorComponent, EquationBuilderComponent],
  templateUrl: './input-panel.component.html',
  styleUrls: ['./input-panel.component.css']
})
export class InputPanelComponent {

  variable1 = 'x';
  variable2 = 'y';
  equation1Data: any = null;
  equation2Data: any = null;

  onVariable1Change(variable: string): void {
    this.variable1 = variable || 'x';
  }

  onVariable2Change(variable: string): void {
    this.variable2 = variable || 'y';
  }
  onEquation1Change(data: any): void {
    this.equation1Data = data;
    console.log('Equation 1:', data);
  }

  onEquation2Change(data: any): void {
    this.equation2Data = data;
    console.log('Equation 2:', data);
  }
  saveSystem(): void {

  const payload = {
    variables: {
      var1: this.variable1,
      var2: this.variable2
    },
    equation1: this.equation1Data,
    equation2: this.equation2Data
  };

  console.log("Sending payload:", payload);

  this.equationApi.saveSystem(payload).subscribe({
    next: (response) => {
      console.log("Saved successfully:", response);
    },
    error: (error) => {
      console.error("Save failed:", error);
    }
  });

}
  constructor(private equationApi: EquationApiService) {}
}
