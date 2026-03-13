import { Component, ElementRef, EventEmitter, Input, OnChanges, Output, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { drawGraph, GraphData } from '../../utils/graph-drawer';

@Component({
  selector: 'app-view-graph-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './view-graph-modal.component.html',
  styleUrl: './view-graph-modal.component.css',
})
export class ViewGraphModalComponent implements OnChanges {
  @Input() isOpen = false;
  @Input() graphData: GraphData | null = null;

  @Output() close = new EventEmitter<void>();

  @ViewChild('canvasEl') canvasRef!: ElementRef<HTMLCanvasElement>;

  onBackdropClick(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.close.emit();
    }
  }

  ngOnChanges(): void {
    if (!this.isOpen) return;
    requestAnimationFrame(() => requestAnimationFrame(() => this.draw()));
  }

  private draw(): void {
    const canvas = this.canvasRef?.nativeElement;
    if (!canvas || !this.graphData || !this.isOpen) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const rect = canvas.getBoundingClientRect();
    if (rect.width <= 0 || rect.height <= 0) return;
    const dpr = window.devicePixelRatio || 1;
    const w = Math.floor(rect.width * dpr);
    const h = Math.floor(rect.height * dpr);
    canvas.width = w;
    canvas.height = h;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
    drawGraph(ctx, this.graphData as GraphData, rect.width, rect.height);
  }
}
