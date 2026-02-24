import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({ providedIn: 'root' })
export class AuthService {

  private usernameSubject = new BehaviorSubject<string | null>(null);
  username$ = this.usernameSubject.asObservable();

  private roleSubject = new BehaviorSubject<string | null>(null);
  role$ = this.roleSubject.asObservable();

  private readySubject = new BehaviorSubject<boolean>(false);
  ready$ = this.readySubject.asObservable();

  constructor(private http: HttpClient) {
    this.restoreSession();
  }

  login(username: string, role: string) {
    this.usernameSubject.next(username);
    this.roleSubject.next(role);
    this.readySubject.next(true);
  }

  logout() {
    this.usernameSubject.next(null);
    this.roleSubject.next(null);
    this.readySubject.next(true);
  }

  isLoggedIn() {
    return this.usernameSubject.value !== null;
  }

  restoreSession() {
    this.http.get<any>('/api/user-session', { withCredentials: true })
      .subscribe({
        next: (res) => {
          this.usernameSubject.next(res.username);
          this.roleSubject.next(res.role);
          this.readySubject.next(true);
        },
        error: () => {
          this.readySubject.next(true);
        }
      });
  }
}