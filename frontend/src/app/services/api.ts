import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ApiService {

private baseUrl = '/api';
  constructor(private http: HttpClient) {}

  applyLeave(data: any) {
    return this.http.post(`${this.baseUrl}/apply-leave`, data, { withCredentials: true });
  }

  getMyLeaves() {
    return this.http.get(`${this.baseUrl}/my-leaves`, { withCredentials: true });
  }

  getAllLeaves() {
    return this.http.get(`${this.baseUrl}/all-leaves`, { withCredentials: true });
  }

  approveLeave(id: string) {
    return this.http.put(`${this.baseUrl}/approve/${id}`, {}, { withCredentials: true });
  }

  rejectLeave(id: string) {
    return this.http.put(`${this.baseUrl}/reject/${id}`, {}, { withCredentials: true });
  }

  updateLeave(id: string, data: any) {
    return this.http.put(`${this.baseUrl}/update/${id}`, data, { withCredentials: true });
  }

  cancelLeave(id: string) {
    return this.http.delete(`${this.baseUrl}/cancel/${id}`, { withCredentials: true });
  }

  login(data: any) {
    return this.http.post(`${this.baseUrl}/login`, data, { withCredentials: true });
  }
}