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
  @Output() methodSelected = new EventEmitter<string>();

  readonly methods = [
    { key: 'elimination', label: 'Elimination', enabled: true },
    { key: 'graphical', label: 'Graphical', enabled: true },
    { key: 'substitution', label: 'Substitution', enabled: false },
    { key: 'comparison', label: 'Comparison', enabled: false }
  ];

  selectMethod(methodKey: string, enabled: boolean): void {
    if (!enabled) {
      return;
    }
    this.methodSelected.emit(methodKey);
  }
}
