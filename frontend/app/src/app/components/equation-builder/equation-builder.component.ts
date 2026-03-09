import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import { Term } from '../../models/term.model';
import { constantToLatex, variableCoeffToLatex } from '../../utils/latex-generator';

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
export class EquationBuilderComponent implements OnInit {

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

  equationLatex = '';

  ngOnInit(): void {
    this.updatePreview();
  }

  onTerm1Change(term: Term): void {
    this.term1 = term;
    this.updatePreview();
  }

  onTerm2Change(term: Term): void {
    this.term2 = term;
    this.updatePreview();
  }

  onConstantChange(term: Term): void {
    this.constant = term;
    this.updatePreview();
  }

  updatePreview(): void {
    const left = `${variableCoeffToLatex(this.term1)}x`;
    const rightVariable = `${variableCoeffToLatex({ ...this.term2, sign: 1 })}y`;
    const operator = this.term2.sign === -1 ? ' - ' : ' + ';
    const constant = constantToLatex(this.constant);

    this.equationLatex = `${left}${operator}${rightVariable} = ${constant}`;
  }
}
