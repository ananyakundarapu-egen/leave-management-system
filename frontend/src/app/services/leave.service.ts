import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class LeaveService {

  private api = environment.apiUrl;

  constructor(private http: HttpClient) {}

  applyLeave(data: any): Observable<any> {
    return this.http.post(`${this.api}/apply-leave`, data, {
      withCredentials: true
    });
  }

  updateLeave(leaveId: string, data: any): Observable<any> {
    return this.http.put(`${this.api}/update/${leaveId}`, data, {
      withCredentials: true
    });
  }

  getMyLeaves(): Observable<any[]> {
    return this.http.get<any[]>(`${this.api}/my-leaves`, {
      withCredentials: true
    });
  }

  cancelLeave(id: string): Observable<any> {
    return this.http.delete(`${this.api}/cancel/${id}`, {
      withCredentials: true
    });
  }

  checkSession(): Observable<any> {
    return this.http.get(`${this.api}/user-session`, {
      withCredentials: true
    });
  }
}