import { Component, EventEmitter, OnDestroy, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { VariableSelectorComponent } from '../variable-selector/variable-selector.component';
import { EquationBuilderComponent } from '../equation-builder/equation-builder.component';
import { EquationApiService } from '../../services/equation-api.service';
import { SolverResponse } from '../../models/solver-response.model';
import { SolverStateService, LayoutMode } from '../../services/solver-state.service';
import { Term } from '../../models/term.model';

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
  /** When status is variable_conflict, the variables used by the existing system. */
  existingVariables: string[] = [];
  layoutMode: LayoutMode = 'rational';
  showModeSwitchConfirm = false;
  pendingMode: LayoutMode | null = null;

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
      }),
      this.state.layoutMode$.subscribe((mode) => {
        this.layoutMode = mode;
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

  onModeClick(mode: LayoutMode): void {
    if (mode === this.layoutMode) return;
    this.pendingMode = mode;
    this.showModeSwitchConfirm = true;
  }

  cancelModeSwitch(): void {
    this.showModeSwitchConfirm = false;
    this.pendingMode = null;
  }

  confirmModeSwitch(): void {
    if (this.pendingMode !== null) {
      this.state.setLayoutMode(this.pendingMode);
      this.showModeSwitchConfirm = false;
      this.pendingMode = null;
    }
  }

  onModeConfirmBackdropClick(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.cancelModeSwitch();
    }
  }

  /** Validation: only visible fields for current layout mode. Invalid blocks Solve. */
  get validationResult(): { valid: boolean; message?: string } {
    const eq1 = this.equation1Data ?? this.initialEquation1;
    const eq2 = this.equation2Data ?? this.initialEquation2;
    if (!eq1 || !eq2) return { valid: true };
    return this.validateEquationsForMode(eq1, eq2, this.layoutMode);
  }

  private validateEquationsForMode(
    eq1: { term1?: Term; term2?: Term; constant?: Term },
    eq2: { term1?: Term; term2?: Term; constant?: Term },
    mode: LayoutMode
  ): { valid: boolean; message?: string } {
    const terms = [
      eq1.term1, eq1.term2, eq1.constant,
      eq2.term1, eq2.term2, eq2.constant
    ].filter(Boolean) as Term[];
    for (const term of terms) {
      const r = this.validateTermForMode(term, mode);
      if (!r.valid) return r;
    }
    return { valid: true };
  }

  private validateTermForMode(term: Term, mode: LayoutMode): { valid: boolean; message?: string } {
    const n = (v: number) => Number.isFinite(v) && v >= 0;
    const p = (v: number) => Number.isFinite(v) && v >= 1;
    switch (mode) {
      case 'rational':
        if (!n(term.numCoeff)) return { valid: false, message: 'Coefficient must be a non-negative number.' };
        break;
      case 'irrational':
        if (!n(term.numCoeff)) return { valid: false, message: 'Numerator coefficient must be a non-negative number.' };
        if (!p(term.numRad)) return { valid: false, message: 'Value under √ must be at least 1.' };
        break;
      case 'fraction':
        if (!n(term.numCoeff)) return { valid: false, message: 'Numerator coefficient must be a non-negative number.' };
        if (!p(term.denCoeff)) return { valid: false, message: 'Denominator must be at least 1.' };
        break;
      case 'fraction_surd':
        if (!n(term.numCoeff)) return { valid: false, message: 'Numerator coefficient must be a non-negative number.' };
        if (!p(term.numRad)) return { valid: false, message: 'Numerator √ value must be at least 1.' };
        if (!p(term.denCoeff)) return { valid: false, message: 'Denominator coefficient must be at least 1.' };
        if (!p(term.denRad)) return { valid: false, message: 'Denominator √ value must be at least 1.' };
        break;
    }
    return { valid: true };
  }

  saveSystem(): void {
    const eq1 = this.equation1Data ?? this.initialEquation1;
    const eq2 = this.equation2Data ?? this.initialEquation2;
    if (!eq1 || !eq2 || this.isSubmitting || !this.canSolve) return;
    const validation = this.validationResult;
    if (!validation.valid) {
      this.errorMessage = validation.message ?? 'Please fix invalid values.';
      return;
    }
    this.errorMessage = '';
    this.existingVariables = [];
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

        if (!response.methods) {
          this.errorMessage = response.message ?? 'Unable to solve system.';
          this.existingVariables = Array.isArray(response.existing_variables) ? response.existing_variables : [];
          return;
        }
        if (!response.solution && response.solution_type !== 'none' && response.solution_type !== 'infinite' && response.solution_type !== 'above_grade') {
          this.errorMessage = response.message ?? 'Unable to solve system.';
          this.existingVariables = Array.isArray(response.existing_variables) ? response.existing_variables : [];
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
