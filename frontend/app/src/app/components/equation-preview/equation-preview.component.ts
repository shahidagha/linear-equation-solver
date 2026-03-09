import { AfterViewInit, Component, ElementRef, Input, OnChanges, SimpleChanges, ViewChild } from '@angular/core';
import katex from 'katex';

@Component({
  selector: 'app-equation-preview',
  standalone: true,
  templateUrl: './equation-preview.component.html',
  styleUrl: './equation-preview.component.css'
})
export class EquationPreviewComponent implements OnChanges, AfterViewInit {

  @Input() equation = '';

  @ViewChild('equationContainer', { static: true })
  equationContainer!: ElementRef<HTMLDivElement>;

  private viewInitialized = false;

  ngAfterViewInit(): void {
    this.viewInitialized = true;
    this.renderEquation();
  }

  ngOnChanges(_changes: SimpleChanges): void {
    this.renderEquation();
  }

  private renderEquation(): void {
    if (!this.viewInitialized || !this.equationContainer) {
      return;
    }

    const container = this.equationContainer.nativeElement;

    if (!this.equation?.trim()) {
      container.textContent = '';
      return;
    }

    try {
      katex.render(this.equation, container, {
        throwOnError: false,
      });
    } catch {
      container.textContent = this.equation;
    }
  }
}
