import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { VariableSelectorComponent } from '../variable-selector/variable-selector.component';
import { EquationBuilderComponent } from '../equation-builder/equation-builder.component';
import { EquationApiService } from '../../services/equation-api.service';
import { SolverResponse } from '../../models/solver-response.model';

@Component({
  selector: 'app-input-panel',
  standalone: true,
  imports: [CommonModule, VariableSelectorComponent, EquationBuilderComponent],
  templateUrl: './input-panel.component.html',
  styleUrls: ['./input-panel.component.css']
})
export class InputPanelComponent {
  @Output() solved = new EventEmitter<SolverResponse>();

  variable1 = 'x';
  variable2 = 'y';
  equation1Data: any = null;
  equation2Data: any = null;
  isSubmitting = false;
  errorMessage = '';

  constructor(private equationApi: EquationApiService) {}

  onVariable1Change(variable: string): void { this.variable1 = variable || 'x'; }
  onVariable2Change(variable: string): void { this.variable2 = variable || 'y'; }
  onEquation1Change(data: any): void { this.equation1Data = data; }
  onEquation2Change(data: any): void { this.equation2Data = data; }

  saveSystem(): void {
    if (!this.equation1Data || !this.equation2Data || this.isSubmitting) return;
    this.errorMessage = '';
    this.isSubmitting = true;

    const payload = {
      variables: { var1: this.variable1, var2: this.variable2 },
      equation1: this.equation1Data,
      equation2: this.equation2Data
    };

    this.equationApi.solveSystem(payload).subscribe({
      next: (response: SolverResponse) => {
        this.isSubmitting = false;
        if (!response) {
          this.errorMessage = 'No response from server.';
          return;
        }
        this.solved.emit(response);
      },
      error: (error) => {
        this.isSubmitting = false;
        this.errorMessage = error?.error?.message ?? 'Server error while solving system.';
      }
    });
  }
}
