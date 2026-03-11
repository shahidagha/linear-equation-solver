import { AfterViewChecked, Component, ElementRef, OnDestroy, OnInit, QueryList, ViewChildren } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { EquationApiService } from '../../services/equation-api.service';
import { SolverStateService } from '../../services/solver-state.service';
import { SolverResponse } from '../../models/solver-response.model';
import { ConfirmDeleteModalComponent } from '../confirm-delete-modal/confirm-delete-modal.component';
import katex from 'katex';
import { equationToLatex } from '../../utils/latex-generator';

@Component({
  selector: 'app-saved-systems',
  standalone: true,
  imports: [CommonModule, FormsModule, ConfirmDeleteModalComponent],
  templateUrl: './saved-systems.component.html',
  styleUrls: ['./saved-systems.component.css']
})
export class SavedSystemsComponent implements OnInit, OnDestroy, AfterViewChecked {
  systems: any[] = [];
  searchTerm = '';
  currentPage = 1;
  pageSize = 8;
  editingSystemId: number | null = null;
  pendingDeleteSystem: any | null = null;
  isDeleting = false;

  private readonly subscriptions: Subscription[] = [];
  @ViewChildren('systemEquation')
  private readonly systemEquationBlocks!: QueryList<ElementRef<HTMLElement>>;

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

  ngAfterViewChecked(): void {
    this.renderSystemEquations();
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
    return `${this.buildEquationLatex(system.equation1, system.variables)} ; ${this.buildEquationLatex(system.equation2, system.variables)}`;
  }

  buildEquationLatex(eq: any, vars: any): string {
    return equationToLatex(eq, vars);
  }

  trackBySystem(index: number, system: any): number {
    return system.id;
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

  private renderSystemEquations(): void {
    if (!this.systemEquationBlocks) {
      return;
    }

    this.systemEquationBlocks.forEach((blockRef) => {
      const block = blockRef.nativeElement;
      const latex = block.dataset['latex'];

      if (!latex || block.dataset['renderedLatex'] === latex) {
        return;
      }

      try {
        katex.render(latex, block, {
          throwOnError: false,
          displayMode: false,
        });
      } catch {
        block.textContent = latex;
      }

      block.dataset['renderedLatex'] = latex;
    });
  }
}
