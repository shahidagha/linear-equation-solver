import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { SolverResponse } from '../models/solver-response.model';

export type PanelMode = 'saved' | 'solution';
export type VerbosityLevel = 'detailed' | 'medium' | 'short';

@Injectable({ providedIn: 'root' })
export class SolverStateService {
  private readonly currentSystemIdSubject = new BehaviorSubject<number | null>(null);
  private readonly solutionSubject = new BehaviorSubject<Record<string, string | number> | null>(null);
  private readonly methodsSubject = new BehaviorSubject<SolverResponse['methods'] | null>(null);
  private readonly graphSubject = new BehaviorSubject<SolverResponse['graph'] | null>(null);
  private readonly selectedMethodSubject = new BehaviorSubject<string>('elimination');
  private readonly verbositySubject = new BehaviorSubject<VerbosityLevel>('detailed');
  private readonly panelModeSubject = new BehaviorSubject<PanelMode>('saved');

  readonly currentSystemId$ = this.currentSystemIdSubject.asObservable();
  readonly solution$ = this.solutionSubject.asObservable();
  readonly methods$ = this.methodsSubject.asObservable();
  readonly graph$ = this.graphSubject.asObservable();
  readonly selectedMethod$ = this.selectedMethodSubject.asObservable();
  readonly verbosity$ = this.verbositySubject.asObservable();
  readonly panelMode$ = this.panelModeSubject.asObservable();

  setResponse(systemId: number | null, response: SolverResponse): void {
    this.currentSystemIdSubject.next(systemId);
    this.solutionSubject.next(response.solution ?? null);
    this.methodsSubject.next(response.methods ?? null);
    this.graphSubject.next(response.graph ?? null);
    this.selectedMethodSubject.next('elimination');
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
    this.panelModeSubject.next('saved');
  }
}
