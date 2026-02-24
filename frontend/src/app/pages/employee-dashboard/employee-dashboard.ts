import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApplyLeaveComponent } from '../apply-leave/apply-leave';
import { LeaveService } from '../../services/leave.service';
import { DatePipe } from '@angular/common';
import { SuccessPopupComponent } from '../../shared/success-popup/success-popup';
import { ConfirmPopupComponent } from '../../shared/confirm-popup/confirm-popup';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-employee-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    ApplyLeaveComponent,
    DatePipe,
    SuccessPopupComponent,
    ConfirmPopupComponent
  ],
  templateUrl: './employee-dashboard.html',
  styleUrl: './employee-dashboard.css',
})
export class EmployeeDashboard implements OnInit {

  showApplyModal = false;
  showSuccessPopup = false;
  showConfirmPopup = false;

  leaves: any[] | null = null; 
  selectedLeave: any = null;
  editingLeave: any = null;
  lastAction: 'create' | 'edit' = 'create';
  constructor(private leaveService: LeaveService, private cdr: ChangeDetectorRef) {}

  ngOnInit() {
  this.leaveService.checkSession().subscribe({
    next: () => {
      this.loadLeaves();  
    },
    error: () => {
      console.log("Session not ready yet");
    }
  });
}
  loadLeaves() {
  this.leaves = null;

  this.leaveService.getMyLeaves().subscribe({
    next: (data: any[]) => {
      console.log("Leaves loaded:", data);
      this.leaves = data;

      this.cdr.detectChanges();
    },
    error: (err) => {
      console.log("Failed to load leaves", err);
      this.leaves = [];

      this.cdr.detectChanges();
    }
  });
}

handleLeaveCreated() {
  this.showSuccessPopup = true;
  this.editingLeave = null;
  this.loadLeaves();
}

  openApplyLeave() {
    this.lastAction = 'create';
    this.showApplyModal = true;
  }

  closeApplyLeave() {
    this.showApplyModal = false;
  }

  withdraw(leave: any) {
    this.selectedLeave = leave;
    this.showConfirmPopup = true;
  }

  editLeave(leave: any) {

  if (leave.status !== 'Pending') return;
  this.lastAction = 'edit';
  this.editingLeave = leave;
  this.showApplyModal = true;
}

confirmDelete() {
  if (!this.selectedLeave) return;

  this.leaveService.cancelLeave(this.selectedLeave.leave_id).subscribe({
    next: () => {
      this.showConfirmPopup = false;
      this.selectedLeave = null;
      this.loadLeaves();
    },

    error: (err) => {
      console.log("Cancel error:", err);

      this.showConfirmPopup = false;
      this.selectedLeave = null;

      if (err.status === 409) {
        alert(err.error?.detail || "Cannot withdraw this leave right now.");
      } else if (err.status === 400) {
        alert(err.error?.detail || "Only pending leaves can be withdrawn.");
      } else {
        alert("Something went wrong while withdrawing leave.");
      }
    }
  });
}

  cancelDelete() {
    this.showConfirmPopup = false;
    this.selectedLeave = null;
  }
  
  isLeaveStarted(leave: any): boolean {
  const today = new Date();
  const startDate = new Date(leave.start_date);

  today.setHours(0,0,0,0);
  startDate.setHours(0,0,0,0);

  return startDate < today;
}
}