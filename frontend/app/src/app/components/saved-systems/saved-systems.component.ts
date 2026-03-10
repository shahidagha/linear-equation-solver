import { Component, OnInit } from '@angular/core';
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

  systems: any[] = [];

  constructor(private equationApi: EquationApiService) {}

  ngOnInit(): void {
    this.loadSystems();
  }

  loadSystems(): void {

    this.equationApi.getSystems().subscribe({

      next: (data: any) => {
        console.log("Loaded systems:", data);
        this.systems = data;
      },

      error: (err) => {
        console.error("Failed to load systems:", err);
      }

    });

  }
    buildEquation(eq: any, vars: any): string {

    const v1 = vars.var1;
    const v2 = vars.var2;

    const t1 = eq.term1.numCoeff * eq.term1.sign;
    const t2 = eq.term2.numCoeff * eq.term2.sign;
    const c  = eq.constant.numCoeff * eq.constant.sign;

    const part1 = `${t1}${v1}`;
    const part2 = t2 >= 0 ? ` + ${t2}${v2}` : ` - ${Math.abs(t2)}${v2}`;

    return `${part1}${part2} = ${c}`;
  }
  showSolution(system: any): void {

    console.log("Open solution for:", system);

  }

  deleteSystem(id: number): void {

    console.log("Delete system:", id);

  }
}