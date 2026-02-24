import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-success-popup',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './success-popup.html',
  styleUrls: ['./success-popup.css']
})
export class SuccessPopupComponent {

  @Input() open = false;
  @Input() message = 'Leave applied successfully';

  @Output() closed = new EventEmitter<void>();

  close() {
    this.closed.emit();
  }

  backdropClick(event: MouseEvent) {
    this.close();
  }
}