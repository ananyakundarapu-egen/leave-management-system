import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login';
import { ManagerDashboardComponent } from './pages/manager-dashboard/manager-dashboard';
import { authGuard } from './services/auth.guard';
import { SignupComponent } from './pages/signup/signup';
import { Layout } from './layout/layout';
import { EmployeeDashboard } from './pages/employee-dashboard/employee-dashboard';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'signup', component: SignupComponent },
  {
    path: '',
    component: Layout,
    canActivate: [authGuard],
    children: [
      { path: 'employee-dashboard', component: EmployeeDashboard },
      { path: 'manager', component: ManagerDashboardComponent },
    ]
  },

  { path: '**', redirectTo: 'login' }
];
