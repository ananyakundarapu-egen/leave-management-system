import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-confirm-popup',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './confirm-popup.html',
  styleUrls: ['./confirm-popup.css']
})
export class ConfirmPopupComponent {

  @Input() open = false;
  @Input() message = 'Are you sure?';

  @Output() confirmed = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();

  confirm() { this.confirmed.emit(); }
  cancel() { this.cancelled.emit(); }

  backdropClick() { this.cancel(); }
}