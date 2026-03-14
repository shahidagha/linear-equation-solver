import { AfterViewChecked, Component, ElementRef, OnDestroy, OnInit, QueryList, ViewChildren } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Subscription } from 'rxjs';
import { EquationApiService } from '../../services/equation-api.service';
import { SolverStateService, LayoutMode } from '../../services/solver-state.service';
import { SolverResponse } from '../../models/solver-response.model';
import { ConfirmDeleteModalComponent } from '../confirm-delete-modal/confirm-delete-modal.component';
import katex from 'katex';
import { equationToLatex } from '../../utils/latex-generator';
import { Term } from '../../models/term.model';

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
  showEditModeSuggestModal = false;
  suggestedLayoutMode: LayoutMode | null = null;

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
    const vars = this.normalizeVariables(system.variables);
    return `${this.buildEquationLatex(system.equation1, vars)} ; ${this.buildEquationLatex(system.equation2, vars)}`;
  }

  buildEquationLatex(eq: any, vars: any): string {
    return equationToLatex(eq, vars);
  }

  trackBySystem(index: number, system: any): number {
    return system.id;
  }

  /** API returns variables as array [var1, var2]; state expects { var1, var2 }. */
  private normalizeVariables(variables: any): { var1: string; var2: string } {
    if (Array.isArray(variables)) {
      return { var1: String(variables[0] ?? 'x'), var2: String(variables[1] ?? 'y') };
    }
    if (variables && typeof variables === 'object' && 'var1' in variables && 'var2' in variables) {
      return { var1: String(variables.var1 ?? 'x'), var2: String(variables.var2 ?? 'y') };
    }
    return { var1: 'x', var2: 'y' };
  }

  showSolution(system: any): void {
    if (!system.stored_response) return;

    this.state.loadSystemForSolution({
      id: system.id,
      variables: this.normalizeVariables(system.variables),
      equation1: system.equation1,
      equation2: system.equation2,
      stored_response: system.stored_response as SolverResponse
    });
  }

  editSystem(system: any): void {
    this.editingSystemId = system.id;
    this.state.loadSystemForEdit({
      id: system.id,
      variables: this.normalizeVariables(system.variables),
      equation1: system.equation1,
      equation2: system.equation2
    });
    const inferred = this.inferLayoutMode(system.equation1, system.equation2);
    if (inferred !== 'fraction_surd') {
      this.suggestedLayoutMode = inferred;
      this.showEditModeSuggestModal = true;
    } else {
      this.suggestedLayoutMode = null;
      this.showEditModeSuggestModal = false;
    }
  }

  /** Infer smallest mode that can represent this system (Rule 6). */
  private inferLayoutMode(eq1: any, eq2: any): LayoutMode {
    const terms: Term[] = [];
    for (const eq of [eq1, eq2]) {
      if (eq?.term1) terms.push(eq.term1);
      if (eq?.term2) terms.push(eq.term2);
      if (eq?.constant) terms.push(eq.constant);
    }
    if (terms.length === 0) return 'fraction_surd';
    const allRational = terms.every((t) => t.numRad === 1 && t.denCoeff === 1 && t.denRad === 1);
    if (allRational) return 'rational';
    const allIrrational = terms.every((t) => t.denCoeff === 1 && t.denRad === 1);
    if (allIrrational) return 'irrational';
    const allFraction = terms.every((t) => t.numRad === 1 && t.denRad === 1);
    if (allFraction) return 'fraction';
    return 'fraction_surd';
  }

  get suggestedModeLabel(): string {
    if (!this.suggestedLayoutMode) return '';
    const labels: Record<LayoutMode, string> = {
      rational: 'Rational',
      irrational: 'Irrational',
      fraction: 'Fraction',
      fraction_surd: 'Fraction surd'
    };
    return labels[this.suggestedLayoutMode];
  }

  cancelEditModeSuggest(): void {
    this.showEditModeSuggestModal = false;
    this.suggestedLayoutMode = null;
  }

  confirmEditModeSuggest(): void {
    if (this.suggestedLayoutMode) {
      this.state.setLayoutMode(this.suggestedLayoutMode);
    }
    this.showEditModeSuggestModal = false;
    this.suggestedLayoutMode = null;
  }

  onEditModeSuggestBackdropClick(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.cancelEditModeSuggest();
    }
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
