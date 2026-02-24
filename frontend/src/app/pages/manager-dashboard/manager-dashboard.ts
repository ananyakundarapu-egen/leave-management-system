import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ApiService } from '../../services/api';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-manager-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './manager-dashboard.html',
  styleUrls: [
  './manager-dashboard.css',
  '../employee-dashboard/employee-dashboard.css'
]
})
export class ManagerDashboardComponent implements OnInit {

  leaves: any[] | null = null;
  searchText: string = '';
  selectedType: string = '';
  leaveTypes: string[] = [];

  constructor(private api: ApiService, private cd: ChangeDetectorRef) {}

  ngOnInit() {
    this.loadLeaves();
  }

  loadLeaves() {
    this.api.getAllLeaves().subscribe({
      next: (data: any) => {
        this.leaves = data || [];
        console.log("Leaves:", this.leaves);
        this.leaveTypes = this.leaves
        ? [...new Set(this.leaves.map(l => l.leave_type))]
        : [];
        this.cd.detectChanges();
      },
      error: (err) => {
        console.error("Failed to load leaves", err);
        this.leaves = [];
        this.cd.detectChanges();
      }
    });
  }

approve(id: string) {
  this.api.approveLeave(id).subscribe({
    next: () => {
      this.loadLeaves();
    },
    error: (err) => {
      console.log("Approve error:", err);

      if (err.status === 409) {
        alert(
          err.error?.detail ||
          "Leave was just created. Please try again in 2–5 minutes."
        );
      } else {
        alert("Something went wrong while approving.");
      }
    }
  });
}

reject(id: string) {
  this.api.rejectLeave(id).subscribe({
    next: () => {
      this.loadLeaves();
    },
    error: (err) => {
      console.log("Reject error:", err);

      if (err.status === 409) {
        alert(
          err.error?.detail ||
          "Leave was just created. Please try again in 2–5 minutes."
        );
      } else {
        alert("Something went wrong while rejecting.");
      }
    }
  });
}

isActionDisabled(leave: any): boolean {

  const today = new Date();
  const startDate = new Date(leave.start_date);

  today.setHours(0, 0, 0, 0);
  startDate.setHours(0, 0, 0, 0);

  return startDate < today|| leave.status !== 'Pending';
}

filteredLeaves() {
  if (!this.leaves) return [];

  const search = this.searchText?.toLowerCase() || '';

  return this.leaves.filter(leave => {

    const employeeId = String(leave.employee_id || '').toLowerCase();
    const leaveId = String(leave.leave_id || '').toLowerCase();
    const type = String(leave.leave_type || '');

    const searchMatch =
      !search ||
      employeeId.includes(search) ||
      leaveId.includes(search);

    const typeMatch =
      !this.selectedType || type === this.selectedType;

    return searchMatch && typeMatch;
  });
}

}