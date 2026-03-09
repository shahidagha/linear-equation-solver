import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

export type FrameKey = 'term1' | 'term2' | 'equals' | 'constant';
export type FramePositions = Record<FrameKey, number>;

@Component({
  selector: 'app-position-controls',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './position-controls.component.html',
  styleUrl: './position-controls.component.css'
})
export class PositionControlsComponent {
  @Input() positions: FramePositions = {
    term1: 1,
    term2: 2,
    equals: 3,
    constant: 4
  };

  @Output() positionsChange = new EventEmitter<FramePositions>();

  readonly controls: Array<{ key: FrameKey; label: string }> = [
    { key: 'term1', label: 'First Term' },
    { key: 'term2', label: 'Second Term' },
    { key: 'equals', label: 'Equals' },
    { key: 'constant', label: 'Constant' }
  ];

  readonly options = [1, 2, 3, 4];

  setPosition(key: FrameKey, position: number): void {
    this.positionsChange.emit({ ...this.positions, [key]: position });
  }
}
