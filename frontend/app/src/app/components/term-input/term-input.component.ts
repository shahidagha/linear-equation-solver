import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Term } from '../../models/term.model';

@Component({
  selector: 'app-term-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './term-input.component.html',
  styleUrl: './term-input.component.css'
})
export class TermInputComponent {
  @Input() label = 'Term';
  @Input() variable = '';
  @Input() set initialTerm(value: Term | null) {
    if (!value) return;
    this.term = { ...value };
    this.updateTerm();
  }

  term: Term = {
    sign: 1,
    numCoeff: 1,
    numRad: 1,
    denCoeff: 1,
    denRad: 1
  };

  @Output() termChange = new EventEmitter<Term>();

  ngOnInit() {
    this.updateTerm();
  }

  updateTerm() {
    this.termChange.emit({ ...this.term });
  }

  selectInputValue(event: FocusEvent): void {
    const input = event.target as HTMLInputElement | null;
    input?.select();
  }

  keepSelection(event: MouseEvent): void {
    event.preventDefault();
  }

  onNumericKeydown(event: KeyboardEvent): void {
    const allowedControlKeys = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'ArrowLeft', 'ArrowRight', 'Home', 'End'];
    if (allowedControlKeys.includes(event.key)) return;
    if (/^[0-9]$/.test(event.key)) return;
    event.preventDefault();
  }

  sanitizeNumericField(key: 'numCoeff' | 'numRad' | 'denCoeff' | 'denRad'): void {
    const rawValue = Number(this.term[key]);
    const minValue = key === 'numCoeff' ? 0 : 1;

    if (!Number.isFinite(rawValue)) {
      this.term[key] = minValue;
      this.updateTerm();
      return;
    }

    const normalized = Math.max(minValue, Math.floor(Math.abs(rawValue)));
    if (this.term[key] !== normalized) {
      this.term[key] = normalized;
    }

    this.updateTerm();
  }
}
