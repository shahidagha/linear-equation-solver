import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { EquationApiService } from '../../services/equation-api.service';
import { SolverStateService } from '../../services/solver-state.service';
import { SolverResponse } from '../../models/solver-response.model';
import { ConfirmDeleteModalComponent } from '../confirm-delete-modal/confirm-delete-modal.component';

@Component({
  selector: 'app-saved-systems',
  standalone: true,
  imports: [CommonModule, FormsModule, ConfirmDeleteModalComponent],
  templateUrl: './saved-systems.component.html',
  styleUrls: ['./saved-systems.component.css']
})
export class SavedSystemsComponent implements OnInit, OnDestroy {
  systems: any[] = [];
  searchTerm = '';
  currentPage = 1;
  pageSize = 8;
  editingSystemId: number | null = null;
  pendingDeleteSystem: any | null = null;
  isDeleting = false;

  private readonly subscriptions: Subscription[] = [];

  constructor(private equationApi: EquationApiService, private readonly state: SolverStateService) {}

  ngOnInit(): void {
    this.loadSystems();
    this.subscriptions.push(
      this.state.savedSystemsRefresh$.subscribe(() => {
        this.editingSystemId = null;
        this.loadSystems();
      }),
      this.state.currentSystemId$.subscribe((systemId) => {
        if (systemId === null) {
          this.editingSystemId = null;
        }
      })
    );
  }

  ngOnDestroy(): void {
    this.subscriptions.forEach((s) => s.unsubscribe());
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

    const terms: string[] = [];
    if (t1 !== 0) {
      const firstCoeff = Math.abs(t1) === 1 ? (t1 < 0 ? '-' : '') : `${t1}`;
      terms.push(`${firstCoeff}${v1}`);
    }

    if (t2 !== 0) {
      const coeff = Math.abs(t2) === 1 ? '' : `${Math.abs(t2)}`;
      if (terms.length === 0) {
        terms.push(`${t2 < 0 ? '-' : ''}${coeff}${v2}`);
      } else {
        terms.push(`${t2 >= 0 ? '+' : '-'} ${coeff}${v2}`);
      }
    }

    const left = terms.length > 0 ? terms.join(' ') : '0';
    return `${left} = ${c}`;
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
    this.editingSystemId = system.id;
    this.state.loadSystemForEdit({
      id: system.id,
      variables: system.variables,
      equation1: system.equation1,
      equation2: system.equation2
    });
  }

  openDeleteModal(system: any): void {
    this.pendingDeleteSystem = system;
  }

  cancelDelete(): void {
    if (this.isDeleting) return;
    this.pendingDeleteSystem = null;
  }

  confirmDelete(): void {
    if (!this.pendingDeleteSystem || this.isDeleting) return;

    const deletingId = this.pendingDeleteSystem.id;
    this.isDeleting = true;

    this.equationApi.deleteSystem(deletingId).subscribe({
      next: () => {
        this.systems = this.systems.filter((system) => system.id !== deletingId);

        if (this.editingSystemId === deletingId) {
          this.state.resetSolutionState();
          this.editingSystemId = null;
        }

        this.pendingDeleteSystem = null;
        this.isDeleting = false;
        this.loadSystems();
      },
      error: () => {
        this.pendingDeleteSystem = null;
        this.isDeleting = false;
        this.loadSystems();
      }
    });
  }
}
