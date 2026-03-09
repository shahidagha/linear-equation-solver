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

  readonly controls: FrameKey[] = ['term1', 'term2', 'equals', 'constant'];
  readonly options = [1, 2, 3, 4];

  setPosition(key: FrameKey, position: number): void {
    if (this.positions[key] === position) {
      return;
    }

    const swapped = this.getSwappedPositions(key, position);
    this.positionsChange.emit(swapped);
  }

  private getSwappedPositions(key: FrameKey, newPosition: number): FramePositions {
    const updated: FramePositions = { ...this.positions };
    const displacedKey = (Object.keys(updated) as FrameKey[]).find(
      (frameKey) => updated[frameKey] === newPosition && frameKey !== key
    );

    if (displacedKey) {
      updated[displacedKey] = updated[key];
    }

    updated[key] = newPosition;

    return updated;
  }
}
