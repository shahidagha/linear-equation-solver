import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';

import { Term } from '../../models/term.model';
import { constantToLatex, variableCoeffToLatex } from '../../utils/latex-generator';
import { Output, EventEmitter } from '@angular/core';
import { TermInputComponent } from '../term-input/term-input.component';
import {
  FrameKey,
  FramePositions,
  PositionControlsComponent
} from '../position-controls/position-controls.component';
import { EquationPreviewComponent } from '../equation-preview/equation-preview.component';

interface FrameItem {
  key: FrameKey;
  label: string;
}

interface SignedExpressionTerm {
  sign: 1 | -1;
  value: string;
}

@Component({
  selector: 'app-equation-builder',
  standalone: true,
  imports: [
    CommonModule,
    DragDropModule,
    TermInputComponent,
    PositionControlsComponent,
    EquationPreviewComponent
  ],
  templateUrl: './equation-builder.component.html',
  styleUrl: './equation-builder.component.css'
})
export class EquationBuilderComponent implements OnInit, OnChanges {
  @Input() title = 'Equation';
  @Input() variable1 = 'x';
  @Input() variable2 = 'y';
   @Output() equationChange = new EventEmitter<any>();
  term1: Term = { sign: 1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 };
  term2: Term = { sign: 1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 };
  constant: Term = { sign: 1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 };

  positions: FramePositions = {
    term1: 1,
    term2: 2,
    equals: 3,
    constant: 4
  };

  readonly frameItems: FrameItem[] = [
    { key: 'term1', label: 'First Term' },
    { key: 'term2', label: 'Second Term' },
    { key: 'equals', label: 'Equals' },
    { key: 'constant', label: 'Constant' }
  ];

  equationLatex = '';

  ngOnInit(): void {
    this.updatePreview();
  }

  ngOnChanges(_changes: SimpleChanges): void {
    this.updatePreview();
  }

  get orderedFrames(): FrameItem[] {
    return [...this.frameItems].sort((a, b) => this.positions[a.key] - this.positions[b.key]);
  }

  get equalsDisplay(): string {
    const equalsPosition = this.positions.equals;

    if (equalsPosition === 1) {
      return '0 =';
    }

    if (equalsPosition === 4) {
      return '= 0';
    }

    return '=';
  }

  onPositionsChange(updated: FramePositions): void {
    this.positions = updated;
    this.updatePreview();
  }

  onFrameDrop(event: CdkDragDrop<FrameItem[]>): void {
    if (event.previousIndex === event.currentIndex) {
      return;
    }

    const reordered = [...this.orderedFrames];
    moveItemInArray(reordered, event.previousIndex, event.currentIndex);

    const nextPositions = { ...this.positions };
    reordered.forEach((frame, index) => {
      nextPositions[frame.key] = index + 1;
    });

    this.positions = nextPositions;
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
    const orderedKeys = [...this.frameItems]
      .sort((a, b) => this.positions[a.key] - this.positions[b.key])
      .map((frame) => frame.key);

    const equalsIndex = orderedKeys.indexOf('equals');
    const leftKeys = orderedKeys.slice(0, equalsIndex);
    const rightKeys = orderedKeys.slice(equalsIndex + 1);

    const leftExpression = this.buildSide(leftKeys);
    const rightExpression = this.buildSide(rightKeys);

    this.equationLatex = `${leftExpression} = ${rightExpression}`;

    this.equationChange.emit({
      positions: this.positions,
      term1: this.term1,
      term2: this.term2,
      constant: this.constant
    });
  }

  private buildSide(keys: FrameKey[]): string {
    const terms = keys
      .map((key) => this.frameKeyToTerm(key))
      .filter((term): term is SignedExpressionTerm => term !== null);

    return this.joinTerms(terms);
  }

  private frameKeyToTerm(key: FrameKey): SignedExpressionTerm | null {
    if (key === 'equals') {
      return null;
    }

    if (key === 'constant') {
      return {
        sign: this.constant.sign as 1 | -1,
        value: constantToLatex({ ...this.constant, sign: 1 })
      };
    }

    if (key === 'term1') {
      return {
        sign: this.term1.sign as 1 | -1,
        value: `${variableCoeffToLatex({ ...this.term1, sign: 1 })}${this.variable1}`
      };
    }

    return {
      sign: this.term2.sign as 1 | -1,
      value: `${variableCoeffToLatex({ ...this.term2, sign: 1 })}${this.variable2}`
    };
  }

  private joinTerms(terms: SignedExpressionTerm[]): string {
    if (terms.length === 0) {
      return '0';
    }

    return terms
      .map((term, index) => {
        if (index === 0) {
          return term.sign === -1 ? `-${term.value}` : term.value;
        }

        return term.sign === -1 ? ` - ${term.value}` : ` + ${term.value}`;
      })
      .join('');
  }
 
}
