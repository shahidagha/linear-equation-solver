import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-confirm-delete-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './confirm-delete-modal.component.html',
  styleUrl: './confirm-delete-modal.component.css'
})
export class ConfirmDeleteModalComponent {
  @Input() isOpen = false;
  @Input() isDeleting = false;
  @Input() title = 'Delete System';
  @Input() message = 'Are you sure you want to delete this system?';

  @Output() cancel = new EventEmitter<void>();
  @Output() confirmDelete = new EventEmitter<void>();

  onBackdropClick(event: MouseEvent): void {
    if (event.target === event.currentTarget && !this.isDeleting) {
      this.cancel.emit();
    }
  }
}
