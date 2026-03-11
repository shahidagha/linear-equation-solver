import { Component, Input, OnChanges, OnInit, SimpleChanges, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';

import { Term } from '../../models/term.model';
import { equationToLatex } from '../../utils/latex-generator';
import { TermInputComponent } from '../term-input/term-input.component';
import { FrameKey, FramePositions, PositionControlsComponent } from '../position-controls/position-controls.component';
import { EquationPreviewComponent } from '../equation-preview/equation-preview.component';

interface FrameItem {
  key: FrameKey;
  label: string;
}

@Component({
  selector: 'app-equation-builder',
  standalone: true,
  imports: [CommonModule, DragDropModule, TermInputComponent, PositionControlsComponent, EquationPreviewComponent],
  templateUrl: './equation-builder.component.html',
  styleUrl: './equation-builder.component.css'
})
export class EquationBuilderComponent implements OnInit, OnChanges {
  @Input() title = 'Equation';
  @Input() variable1 = 'x';
  @Input() variable2 = 'y';
  @Input() initialEquation: any = null;
  @Output() equationChange = new EventEmitter<any>();

  term1: Term = { sign: 1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 };
  term2: Term = { sign: 1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 };
  constant: Term = { sign: 1, numCoeff: 1, numRad: 1, denCoeff: 1, denRad: 1 };

  positions: FramePositions = { term1: 1, term2: 2, equals: 3, constant: 4 };

  readonly frameItems: FrameItem[] = [
    { key: 'term1', label: 'First Term' },
    { key: 'term2', label: 'Second Term' },
    { key: 'equals', label: 'Equals' },
    { key: 'constant', label: 'Constant' }
  ];

  equationLatex = '';

  ngOnInit(): void {
    this.applyInitialEquation();
    this.updatePreview();
  }

  ngOnChanges(_changes: SimpleChanges): void {
    this.applyInitialEquation();
    this.updatePreview();
  }

  get orderedFrames(): FrameItem[] {
    return [...this.frameItems].sort((a, b) => this.positions[a.key] - this.positions[b.key]);
  }

  get equalsDisplay(): string {
    if (this.positions.equals === 1) return '0 =';
    if (this.positions.equals === 4) return '= 0';
    return '=';
  }

  onPositionsChange(updated: FramePositions): void {
    this.positions = updated;
    this.updatePreview();
  }

  onFrameDrop(event: CdkDragDrop<FrameItem[]>): void {
    if (event.previousIndex === event.currentIndex) return;

    const reordered = [...this.orderedFrames];
    moveItemInArray(reordered, event.previousIndex, event.currentIndex);

    const nextPositions = { ...this.positions };
    reordered.forEach((frame, index) => {
      nextPositions[frame.key] = index + 1;
    });

    this.positions = nextPositions;
    this.updatePreview();
  }

  onTerm1Change(term: Term): void { this.term1 = term; this.updatePreview(); }
  onTerm2Change(term: Term): void { this.term2 = term; this.updatePreview(); }
  onConstantChange(term: Term): void { this.constant = term; this.updatePreview(); }

  updatePreview(): void {
    this.equationLatex = equationToLatex(
      {
        positions: this.positions,
        term1: this.term1,
        term2: this.term2,
        constant: this.constant,
      },
      {
        var1: this.variable1,
        var2: this.variable2,
      }
    );
    this.equationChange.emit({ positions: this.positions, term1: this.term1, term2: this.term2, constant: this.constant });
  }

  private applyInitialEquation(): void {
    if (!this.initialEquation) return;

    this.positions = this.initialEquation.positions ?? { term1: 1, term2: 2, equals: 3, constant: 4 };
    this.term1 = this.initialEquation.term1 ?? this.term1;
    this.term2 = this.initialEquation.term2 ?? this.term2;
    this.constant = this.initialEquation.constant ?? this.constant;
  }
}
