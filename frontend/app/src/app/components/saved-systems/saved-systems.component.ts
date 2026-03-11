import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { EquationApiService } from '../../services/equation-api.service';

@Component({
  selector: 'app-saved-systems',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './saved-systems.component.html',
  styleUrls: ['./saved-systems.component.css']
})
export class SavedSystemsComponent implements OnInit {
  @Output() systemSelected = new EventEmitter<any>();

  systems: any[] = [];

  constructor(private equationApi: EquationApiService) {}

  ngOnInit(): void {
    this.loadSystems();
  }

  loadSystems(): void {
    this.equationApi.getSystems().subscribe({
      next: (data: any) => {
        this.systems = data;
      },
      error: () => {
        this.systems = [];
      }
    });
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
