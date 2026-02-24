import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { signInWithEmailAndPassword, signOut } from "firebase/auth";
import { auth } from '../../services/firebase';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class LoginComponent {
  username = '';
  password = '';
  error = '';
  usernameTouched = false;
  passwordTouched = false;
  showPassword: boolean = false;

  constructor(
    private router: Router,
    private http: HttpClient,
    private authService: AuthService
  ) {}

  isFormValid(): boolean {
    return this.username.trim() !== '' && this.password.trim() !== '';
  }

  togglePassword() {
  this.showPassword = !this.showPassword;
  }
  async login() {

    await signOut(auth).catch(() => {});

    if (!this.username || !this.password) return;

    try {
      const userCredential = await signInWithEmailAndPassword(
        auth,
        this.username,
        this.password
      );

      const idToken = await userCredential.user.getIdToken();

 this.http.post<any>(
  '/api/login',
  { id_token: idToken },
  { withCredentials: true }
)
.subscribe({
  next: (res) => {

    this.authService.login(res.username, res.role);

    if (res.role === 'manager') {
      this.router.navigate(['/manager']);
    } else {
      this.router.navigate(['/employee-dashboard']);
    }

  },
  error: () => {
    alert("Server verification failed");
  }
});

  } catch (error: any) {

  console.log(error); 

  if (error.code === 'auth/invalid-credential') {
    alert("Invalid email or password. Please try again.");
  }
  else if (error.code === 'auth/invalid-email') {
    alert("Invalid email format.");
  }
  else if (error.code === 'auth/too-many-requests') {
    alert("Too many attempts. Please try again later.");
  }
  else {
    alert("Login failed. Please try again.");
  }
}
  }
}