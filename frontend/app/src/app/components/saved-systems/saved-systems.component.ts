import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { EquationApiService } from '../../services/equation-api.service';
import { SolverStateService } from '../../services/solver-state.service';
import { SolverResponse } from '../../models/solver-response.model';

@Component({
  selector: 'app-saved-systems',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './saved-systems.component.html',
  styleUrls: ['./saved-systems.component.css']
})
export class SavedSystemsComponent implements OnInit, OnDestroy {
  systems: any[] = [];
  searchTerm = '';
  currentPage = 1;
  pageSize = 8;

  private refreshSubscription?: Subscription;

  constructor(private equationApi: EquationApiService, private readonly state: SolverStateService) {}

  ngOnInit(): void {
    this.loadSystems();
    this.refreshSubscription = this.state.savedSystemsRefresh$.subscribe(() => {
      this.loadSystems();
    });
  }

  ngOnDestroy(): void {
    this.refreshSubscription?.unsubscribe();
  }

  loadSystems(): void {
    this.equationApi.getSystems().subscribe({
      next: (data: any) => {
        this.systems = data;
        this.currentPage = 1;
      },
      error: () => {
        this.systems = [];
      }
    });
  }

  get filteredSystems(): any[] {
    const normalizedSearch = this.searchTerm.trim().toLowerCase();
    if (!normalizedSearch) return this.systems;
    return this.systems.filter((system) => this.buildSystemText(system).toLowerCase().includes(normalizedSearch));
  }

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.filteredSystems.length / this.pageSize));
  }

  get pagedSystems(): any[] {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.filteredSystems.slice(start, start + this.pageSize);
  }

  buildSystemText(system: any): string {
    return `${this.buildEquation(system.equation1, system.variables)} ; ${this.buildEquation(system.equation2, system.variables)}`;
  }

  buildEquation(eq: any, vars: any): string {
    const [v1, v2] = [vars.var1, vars.var2];
    const t1 = eq.term1.numCoeff * eq.term1.sign;
    const t2 = eq.term2.numCoeff * eq.term2.sign;
    const c = eq.constant.numCoeff * eq.constant.sign;
    const firstCoeff = Math.abs(t1) === 1 ? (t1 < 0 ? '-' : '') : `${t1}`;
    const secondCoeffAbs = Math.abs(t2) === 1 ? '' : `${Math.abs(t2)}`;
    return `${firstCoeff}${v1}${t2 >= 0 ? ' + ' : ' - '}${secondCoeffAbs}${v2} = ${c}`;
  }

  showSolution(system: any): void {
    if (!system.stored_response) return;

    this.state.loadSystemForSolution({
      id: system.id,
      variables: system.variables,
      equation1: system.equation1,
      equation2: system.equation2,
      stored_response: system.stored_response as SolverResponse
    });
  }

  editSystem(system: any): void {
    this.state.loadSystemForEdit({
      id: system.id,
      variables: system.variables,
      equation1: system.equation1,
      equation2: system.equation2
    });
  }
}
