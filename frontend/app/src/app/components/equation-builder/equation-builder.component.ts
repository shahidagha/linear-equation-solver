import { Component, Input, OnChanges, OnInit, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';

import { Term } from '../../models/term.model';
import { constantToLatex, variableCoeffToLatex } from '../../utils/latex-generator';

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
    const left = `${variableCoeffToLatex(this.term1)}${this.variable1}`;
    const rightVariable = `${variableCoeffToLatex({ ...this.term2, sign: 1 })}${this.variable2}`;
    const operator = this.term2.sign === -1 ? ' - ' : ' + ';
    const constant = constantToLatex(this.constant);

    this.equationLatex = `${left}${operator}${rightVariable} = ${constant}`;
  }
}
