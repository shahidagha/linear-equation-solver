import { Component, EventEmitter, OnDestroy, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { VariableSelectorComponent } from '../variable-selector/variable-selector.component';
import { EquationBuilderComponent } from '../equation-builder/equation-builder.component';
import { EquationApiService } from '../../services/equation-api.service';
import { SolverResponse } from '../../models/solver-response.model';
import { SolverStateService } from '../../services/solver-state.service';

@Component({
  selector: 'app-input-panel',
  standalone: true,
  imports: [CommonModule, VariableSelectorComponent, EquationBuilderComponent],
  templateUrl: './input-panel.component.html',
  styleUrls: ['./input-panel.component.css']
})
export class InputPanelComponent implements OnInit, OnDestroy {
  @Output() solved = new EventEmitter<SolverResponse>();

  variable1 = 'x';
  variable2 = 'y';
  equation1Data: any = null;
  equation2Data: any = null;
  initialEquation1: any = null;
  initialEquation2: any = null;
  canSolve = true;
  currentSystemId: number | null = null;
  isSubmitting = false;
  errorMessage = '';

  private readonly subscriptions: Subscription[] = [];

  constructor(private equationApi: EquationApiService, private readonly state: SolverStateService) {}

  ngOnInit(): void {
    this.subscriptions.push(
      this.state.variables$.subscribe((variables) => {
        this.variable1 = variables.var1 || 'x';
        this.variable2 = variables.var2 || 'y';
      }),
      this.state.equations$.subscribe((equations) => {
        this.initialEquation1 = equations.equation1;
        this.initialEquation2 = equations.equation2;
      }),
      this.state.canSolve$.subscribe((canSolve) => {
        this.canSolve = canSolve;
      }),
      this.state.currentSystemId$.subscribe((systemId) => {
        this.currentSystemId = systemId;
      })
    );
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach((s) => s.unsubscribe());
  }

  onVariable1Change(variable: string): void { this.variable1 = variable || 'x'; }
  onVariable2Change(variable: string): void { this.variable2 = variable || 'y'; }
  onEquation1Change(data: any): void { this.equation1Data = data; }
  onEquation2Change(data: any): void { this.equation2Data = data; }

  saveSystem(): void {
    const eq1 = this.equation1Data ?? this.initialEquation1;
    const eq2 = this.equation2Data ?? this.initialEquation2;
    if (!eq1 || !eq2 || this.isSubmitting || !this.canSolve) return;
    this.errorMessage = '';
    this.isSubmitting = true;

    const payload = {
      variables: { var1: this.variable1, var2: this.variable2 },
      equation1: eq1,
      equation2: eq2,
      system_id: this.currentSystemId ?? undefined
    };

    this.state.setBuilderState(payload);

    this.equationApi.solveSystem(payload).subscribe({
      next: (response: SolverResponse | any) => {
        this.isSubmitting = false;
        if (!response) {
          this.errorMessage = 'No response from server.';
          return;
        }

        if (!response.solution) {
          this.errorMessage = response.message ?? 'Unable to solve system.';
          return;
        }

        this.solved.emit(response as SolverResponse);
      },
      error: (error) => {
        this.isSubmitting = false;
        this.errorMessage = error?.error?.message ?? 'Server error while solving system.';
      }
    });
  }
}
