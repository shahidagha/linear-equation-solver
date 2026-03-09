import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Term } from '../../models/term.model';
import { termToLatex } from '../../utils/latex-generator';

import { TermInputComponent } from '../term-input/term-input.component';
import { PositionControlsComponent } from '../position-controls/position-controls.component';
import { EquationPreviewComponent } from '../equation-preview/equation-preview.component';

@Component({
  selector: 'app-equation-builder',
  standalone: true,
  imports: [
    CommonModule,
    TermInputComponent,
    PositionControlsComponent,
    EquationPreviewComponent
  ],
  templateUrl: './equation-builder.component.html',
  styleUrl: './equation-builder.component.css'
})
export class EquationBuilderComponent {

  // initialize default terms so preview works immediately
  term1: Term = {
    sign: 1,
    numCoeff: 1,
    numRad: 1,
    denCoeff: 1,
    denRad: 1
  };

  term2: Term = {
    sign: 1,
    numCoeff: 1,
    numRad: 1,
    denCoeff: 1,
    denRad: 1
  };

  constant: Term = {
    sign: 1,
    numCoeff: 1,
    numRad: 1,
    denCoeff: 1,
    denRad: 1
  };

  equationLatex: string = '';

  updatePreview() {

  const t1 = termToLatex(this.term1);
  const t2 = termToLatex(this.term2);
  const c = termToLatex(this.constant);

  let equation = `${t1}x`;

  if (this.term2.sign === -1) {
    equation += ` - ${t2}y`;
  } else {
    equation += ` + ${t2}y`;
  }

  equation += ` = ${c}`;

  this.equationLatex = equation;

  console.log("EQUATION:", this.equationLatex);
}

}