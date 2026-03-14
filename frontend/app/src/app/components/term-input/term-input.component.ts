import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Term } from '../../models/term.model';
import { LayoutMode } from '../../services/solver-state.service';

@Component({
  selector: 'app-term-input',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './term-input.component.html',
  styleUrl: './term-input.component.css'
})
export class TermInputComponent implements OnChanges {
  @Input() label = 'Term';
  @Input() variable = '';
  @Input() layoutMode: LayoutMode = 'rational';
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

  ngOnChanges(changes: SimpleChanges): void {
    const modeChange = changes['layoutMode'];
    if (modeChange && !modeChange.firstChange && modeChange.previousValue !== modeChange.currentValue) {
      this.applyModeMapping(this.layoutMode);
      this.updateTerm();
    }
  }

  ngOnInit(): void {
    this.updateTerm();
  }

  /** Set hidden fields to 1 when switching to a simpler mode. */
  private applyModeMapping(mode: LayoutMode): void {
    switch (mode) {
      case 'rational':
        this.term.numRad = 1;
        this.term.denCoeff = 1;
        this.term.denRad = 1;
        break;
      case 'irrational':
        this.term.denCoeff = 1;
        this.term.denRad = 1;
        break;
      case 'fraction':
        this.term.numRad = 1;
        this.term.denRad = 1;
        break;
      case 'fraction_surd':
        break;
    }
  }

  updateTerm(): void {
    const out = this.termForEmit();
    this.termChange.emit(out);
  }

  /** Emit term with hidden fields set to 1 per current mode (Rule 9 / Option D). */
  private termForEmit(): Term {
    const t = { ...this.term };
    switch (this.layoutMode) {
      case 'rational':
        t.numRad = 1;
        t.denCoeff = 1;
        t.denRad = 1;
        break;
      case 'irrational':
        t.denCoeff = 1;
        t.denRad = 1;
        break;
      case 'fraction':
        t.numRad = 1;
        t.denRad = 1;
        break;
      case 'fraction_surd':
        break;
    }
    return t;
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
