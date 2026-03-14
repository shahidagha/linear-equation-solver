import { Injectable } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';
import { SolverResponse } from '../models/solver-response.model';

export interface BuilderState {
  variables: {
    var1: string;
    var2: string;
  };
  equation1: unknown;
  equation2: unknown;
}

export type PanelMode = 'saved' | 'solution';
export type VerbosityLevel = 'detailed' | 'medium' | 'short';

export type LayoutMode = 'rational' | 'irrational' | 'fraction' | 'fraction_surd';

@Injectable({ providedIn: 'root' })
export class SolverStateService {
  private readonly defaultVariables: BuilderState['variables'] = { var1: 'x', var2: 'y' };
  private readonly currentSystemIdSubject = new BehaviorSubject<number | null>(null);
  private readonly variablesSubject = new BehaviorSubject<BuilderState['variables']>(this.defaultVariables);
  private readonly equationsSubject = new BehaviorSubject<{ equation1: unknown; equation2: unknown }>({
    equation1: this.createDefaultEquation(),
    equation2: this.createDefaultEquation()
  });
  private readonly solutionSubject = new BehaviorSubject<Record<string, string | number> | null>(null);
  private readonly methodsSubject = new BehaviorSubject<SolverResponse['methods'] | null>(null);
  private readonly graphSubject = new BehaviorSubject<SolverResponse['graph'] | null>(null);
  private readonly selectedMethodSubject = new BehaviorSubject<string>('elimination');
  private readonly verbositySubject = new BehaviorSubject<VerbosityLevel>('detailed');
  private readonly panelModeSubject = new BehaviorSubject<PanelMode>('saved');
  private readonly canSolveSubject = new BehaviorSubject<boolean>(true);
  private readonly savedSystemsRefreshSubject = new Subject<void>();
  private readonly layoutModeSubject = new BehaviorSubject<LayoutMode>('rational');

  readonly currentSystemId$ = this.currentSystemIdSubject.asObservable();
  readonly variables$ = this.variablesSubject.asObservable();
  readonly equations$ = this.equationsSubject.asObservable();
  readonly solution$ = this.solutionSubject.asObservable();
  readonly methods$ = this.methodsSubject.asObservable();
  readonly graph$ = this.graphSubject.asObservable();
  readonly selectedMethod$ = this.selectedMethodSubject.asObservable();
  readonly verbosity$ = this.verbositySubject.asObservable();
  readonly panelMode$ = this.panelModeSubject.asObservable();
  readonly canSolve$ = this.canSolveSubject.asObservable();
  readonly savedSystemsRefresh$ = this.savedSystemsRefreshSubject.asObservable();
  readonly layoutMode$ = this.layoutModeSubject.asObservable();

  getCurrentSystemId(): number | null {
    return this.currentSystemIdSubject.value;
  }

  setBuilderState(builder: BuilderState): void {
    this.variablesSubject.next(builder.variables);
    this.equationsSubject.next({ equation1: builder.equation1, equation2: builder.equation2 });
  }

  loadSystemForSolution(system: {
    id: number;
    variables: BuilderState['variables'];
    equation1: unknown;
    equation2: unknown;
    stored_response: SolverResponse;
  }): void {
    this.currentSystemIdSubject.next(system.id);
    this.setBuilderState({
      variables: system.variables,
      equation1: system.equation1,
      equation2: system.equation2
    });
    this.solutionSubject.next(system.stored_response.solution ?? null);
    this.methodsSubject.next(system.stored_response.methods ?? null);
    this.graphSubject.next(system.stored_response.graph ?? null);
    this.selectedMethodSubject.next('elimination');
    this.verbositySubject.next('detailed');
    this.canSolveSubject.next(false);
    this.panelModeSubject.next('solution');
  }

  loadSystemForEdit(system: {
    id: number;
    variables: BuilderState['variables'];
    equation1: unknown;
    equation2: unknown;
  }): void {
    this.currentSystemIdSubject.next(system.id);
    this.setBuilderState({
      variables: system.variables,
      equation1: system.equation1,
      equation2: system.equation2
    });
    this.solutionSubject.next(null);
    this.methodsSubject.next(null);
    this.graphSubject.next(null);
    this.selectedMethodSubject.next('elimination');
    this.verbositySubject.next('detailed');
    this.canSolveSubject.next(true);
    this.panelModeSubject.next('saved');
    this.layoutModeSubject.next('fraction_surd');
  }

  setResponse(systemId: number | null, response: SolverResponse): void {
    this.currentSystemIdSubject.next(systemId);
    this.solutionSubject.next(response.solution ?? null);
    this.methodsSubject.next(response.methods ?? null);
    this.graphSubject.next(response.graph ?? null);
    this.selectedMethodSubject.next('elimination');
    this.verbositySubject.next('detailed');
    this.canSolveSubject.next(true);
    this.panelModeSubject.next('solution');
    this.savedSystemsRefreshSubject.next();
  }

  setSelectedMethod(method: string): void {
    this.selectedMethodSubject.next(method);
  }

  setVerbosity(level: VerbosityLevel): void {
    this.verbositySubject.next(level);
  }

  setPanelMode(mode: PanelMode): void {
    this.panelModeSubject.next(mode);
  }

  getLayoutMode(): LayoutMode {
    return this.layoutModeSubject.value;
  }

  setLayoutMode(mode: LayoutMode): void {
    this.layoutModeSubject.next(mode);
  }

  resetSolutionState(): void {
    this.currentSystemIdSubject.next(null);
    this.variablesSubject.next({ ...this.defaultVariables });
    this.equationsSubject.next({
      equation1: this.createDefaultEquation(),
      equation2: this.createDefaultEquation()
    });
    this.solutionSubject.next(null);
    this.methodsSubject.next(null);
    this.graphSubject.next(null);
    this.selectedMethodSubject.next('elimination');
    this.verbositySubject.next('detailed');
    this.canSolveSubject.next(true);
    this.panelModeSubject.next('saved');
    this.savedSystemsRefreshSubject.next();
  }

  private createDefaultEquation(): unknown {
    return {
      positions: { term1: 1, term2: 2, equals: 3, constant: 4 },
      term1: { sign: 1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 },
      term2: { sign: 1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 },
      constant: { sign: 1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 }
    };
  }
}
