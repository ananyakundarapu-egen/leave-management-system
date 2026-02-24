import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { AuthService } from './auth';
import { map, catchError, of } from 'rxjs';

export const authGuard: CanActivateFn = () => {

  const router = inject(Router);
  const http = inject(HttpClient);
  const auth = inject(AuthService);

return http.get<any>('/api/user-session', { withCredentials: true })
    .pipe(
      map(res => {
        auth.login(res.username, res.role);
        return true;
      }),
      catchError(() => {
        router.navigate(['/login']);
        return of(false);
      })
    );
};