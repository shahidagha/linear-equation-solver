import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
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

@Injectable({ providedIn: 'root' })
export class SolverStateService {
  private readonly currentSystemIdSubject = new BehaviorSubject<number | null>(null);
  private readonly variablesSubject = new BehaviorSubject<BuilderState['variables']>({ var1: 'x', var2: 'y' });
  private readonly equationsSubject = new BehaviorSubject<{ equation1: unknown; equation2: unknown }>({
    equation1: null,
    equation2: null
  });
  private readonly solutionSubject = new BehaviorSubject<Record<string, string | number> | null>(null);
  private readonly methodsSubject = new BehaviorSubject<SolverResponse['methods'] | null>(null);
  private readonly graphSubject = new BehaviorSubject<SolverResponse['graph'] | null>(null);
  private readonly selectedMethodSubject = new BehaviorSubject<string>('elimination');
  private readonly verbositySubject = new BehaviorSubject<VerbosityLevel>('detailed');
  private readonly panelModeSubject = new BehaviorSubject<PanelMode>('saved');
  private readonly canSolveSubject = new BehaviorSubject<boolean>(true);

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

  clearSolution(): void {
    this.currentSystemIdSubject.next(null);
    this.solutionSubject.next(null);
    this.methodsSubject.next(null);
    this.graphSubject.next(null);
    this.selectedMethodSubject.next('elimination');
    this.verbositySubject.next('detailed');
    this.canSolveSubject.next(true);
    this.panelModeSubject.next('saved');
  }
}
