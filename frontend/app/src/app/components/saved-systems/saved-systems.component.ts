import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { EquationApiService } from '../../services/equation-api.service';

@Component({
  selector: 'app-saved-systems',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './saved-systems.component.html',
  styleUrls: ['./saved-systems.component.css']
})
export class SavedSystemsComponent implements OnInit {
  @Output() systemSelected = new EventEmitter<any>();

  systems: any[] = [];
  searchTerm = '';
  currentPage = 1;
  readonly pageSize = 8;

  constructor(private equationApi: EquationApiService) {}

  ngOnInit(): void {
    this.loadSystems();
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

    if (!normalizedSearch) {
      return this.systems;
    }

    return this.systems.filter((system) => {
      const combined = this.buildSystemText(system).toLowerCase();
      return combined.includes(normalizedSearch);
    });
  }

  get totalPages(): number {
    return Math.max(1, Math.ceil(this.filteredSystems.length / this.pageSize));
  }

  get pagedSystems(): any[] {
    const start = (this.currentPage - 1) * this.pageSize;
    return this.filteredSystems.slice(start, start + this.pageSize);
  }

  onSearchChange(): void {
    this.currentPage = 1;
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage -= 1;
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage += 1;
    }
  }

  buildSystemText(system: any): string {
    const eq1 = this.buildEquation(system.equation1, system.variables);
    const eq2 = this.buildEquation(system.equation2, system.variables);
    return `${eq1} ; ${eq2}`;
  }

  buildEquation(eq: any, vars: any): string {
    const v1 = vars.var1;
    const v2 = vars.var2;

    const t1 = eq.term1.numCoeff * eq.term1.sign;
    const t2 = eq.term2.numCoeff * eq.term2.sign;
    const c = eq.constant.numCoeff * eq.constant.sign;

    const firstCoeff = Math.abs(t1) === 1 ? (t1 < 0 ? '-' : '') : `${t1}`;
    const secondCoeffAbs = Math.abs(t2) === 1 ? '' : `${Math.abs(t2)}`;
    const part1 = `${firstCoeff}${v1}`;
    const part2 = t2 >= 0 ? ` + ${secondCoeffAbs}${v2}` : ` - ${secondCoeffAbs}${v2}`;

    return `${part1}${part2} = ${c}`;
  }

  showSolution(system: any): void {
    this.systemSelected.emit(system);
  }
}
