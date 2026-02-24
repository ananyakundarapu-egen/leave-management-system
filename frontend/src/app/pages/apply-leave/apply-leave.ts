import { Component, EventEmitter, Input, Output, OnChanges,SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { LeaveService } from '../../services/leave.service';

@Component({
  selector: 'app-apply-leave',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './apply-leave.html',
  styleUrls: ['./apply-leave.css']
})
export class ApplyLeaveComponent implements OnChanges {

  @Input() isOpen = false;
  @Input() editData: any = null;
  @Output() closed = new EventEmitter<void>();
  @Output() leaveCreated = new EventEmitter<void>();
  showSuccess = false;
  submitted=false;
  constructor(private leaveService: LeaveService) {}

  today = new Date().toISOString().split('T')[0];
  minEndDate = this.today;
  serverError: string = ''; 
  form = {
    type: '',
    start_date: '',
    end_date: '',
    reason: ''
  };

  close() {
    this.closed.emit();
  }

  onBackdropClick(event: MouseEvent) {
    this.close();
  }

  onStartDateChange() {
  if (this.form.start_date) {
    this.minEndDate = this.form.start_date;
  }
  if (this.form.end_date && this.form.end_date < this.form.start_date) {
    this.form.end_date = '';
  }
}

ngOnChanges(changes: SimpleChanges) {
  if (changes['editData'] && this.editData) {

    this.form = {
      type: this.editData.leave_type,
      start_date: this.editData.start_date?.split('T')[0] || '',
      end_date: this.editData.end_date?.split('T')[0] || '',
      reason: this.editData.reason
    };

    this.minEndDate = this.form.start_date || this.today;
  }
}

submitLeave(formRef: any) {

  this.submitted = true;
  if (formRef.invalid) return;

  const payload = {
    leave_type: this.form.type,
    start_date: this.form.start_date,
    end_date: this.form.end_date,
    reason: this.form.reason
  };

  if (this.editData) {

    this.leaveService.updateLeave(this.editData.leave_id, payload).subscribe({
      next: () => {
        formRef.resetForm();
        this.resetForm();
        this.submitted = false;
        this.editData = null;
        this.leaveCreated.emit();
        this.close();
      },
      error: (err) => {
        alert(err.error?.detail || 'Cannot edit this leave');
      }
    });

  } else {

    this.leaveService.applyLeave(payload).subscribe({
      next: () => {
        formRef.resetForm();
        this.resetForm();
        this.submitted = false;
        this.leaveCreated.emit();
        this.close();
      },
      error: (err) => {
        alert(err.error?.detail || 'Something went wrong');
      }
    });

  }
}

  private resetForm() {
    this.form = {
      type: '',
      start_date: '',
      end_date: '',
      reason: ''
    };
  }

closeSuccess() {
  this.leaveCreated.emit();
  this.close();
}
}