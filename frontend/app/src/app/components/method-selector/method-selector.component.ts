import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-method-selector',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './method-selector.component.html',
  styleUrl: './method-selector.component.css'
})
export class MethodSelectorComponent {
  @Input() selectedMethod = 'elimination';
  @Input() disabled = false;
  @Output() methodSelected = new EventEmitter<string>();

  readonly methods = [
    { key: 'elimination', label: 'Elimination' },
    { key: 'graphical', label: 'Graphical' },
    { key: 'substitution', label: 'Substitution' },
    { key: 'cramer', label: 'Cramer' }
  ];

  selectMethod(methodKey: string): void {
    if (this.disabled) return;
    this.methodSelected.emit(methodKey);
  }
}
