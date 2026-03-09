import { Component, Input, ElementRef, OnChanges } from '@angular/core';
import katex from 'katex';

@Component({
  selector: 'app-equation-preview',
  standalone: true,
  templateUrl: './equation-preview.component.html',
  styleUrl: './equation-preview.component.css'
})
export class EquationPreviewComponent implements OnChanges {

  @Input() equation: string = '';

  constructor(private el: ElementRef) {}

  ngOnChanges() {

    const container = this.el.nativeElement.querySelector('#equation');

    if (!container) return;

    if (!this.equation) {
      container.innerHTML = '';
      return;
    }

    try {
      katex.render(this.equation, container);
    } catch {
      container.innerHTML = this.equation;
    }

  }

}