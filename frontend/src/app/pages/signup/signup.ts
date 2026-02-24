import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { createUserWithEmailAndPassword } from "firebase/auth";
import { HttpClient } from '@angular/common/http';
import { auth } from '../../services/firebase';
import { AuthService } from '../../services/auth';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-signup',
  standalone: true,
  imports: [FormsModule, CommonModule, RouterLink],
  templateUrl: './signup.html',
  styleUrl: '../login/login.css'
})
export class SignupComponent {

  firstName = '';
  lastName = '';
  email = '';
  password = '';
  confirmPassword = '';
  empId = '';

  firstNameTouched = false;
  lastNameTouched = false;
  emailTouched = false;
  passwordTouched = false;
  confirmPasswordTouched = false;
  empIdTouched = false;
  showPassword: boolean = false;
  showConfirmPassword: boolean = false;
  emailExistsError = '';
  empIdExistsError = '';

  constructor(
    private router: Router,
    private http: HttpClient,
    private authService: AuthService,
    private cd: ChangeDetectorRef 
  ) {}

  isFormValid(): boolean {

  const empPattern = /^EMP[0-9]+$/;

  return (
    this.firstName.trim() !== '' &&
    this.lastName.trim() !== '' &&
    this.email.trim() !== '' &&
    empPattern.test(this.empId.trim()) &&
    this.password.trim() !== '' &&
    this.confirmPassword.trim() !== '' &&
    this.password === this.confirmPassword
  );
}

  togglePassword() {
  this.showPassword = !this.showPassword;
  }

  toggleConfirmPassword() {
  this.showConfirmPassword = !this.showConfirmPassword;
  }

  formatEmpId() {
  this.empId = this.empId.toUpperCase();
}

 async signup() {

  if (!this.isFormValid()) return;

  this.emailExistsError = '';
  this.empIdExistsError = '';

  try {

    const userCredential = await createUserWithEmailAndPassword(
      auth,
      this.email,
      this.password
    );

    const idToken = await userCredential.user.getIdToken();

    this.http.post<any>(
        '/api/register',
      {
        id_token: idToken,
        first_name: this.firstName,
        last_name: this.lastName,
        employee_id: this.empId.trim()
      },
      { withCredentials: true }
    )
.subscribe({
  next: (res) => {
    this.authService.login(res.username, res.role);
    this.router.navigate(['/employee-dashboard']);
  },

error: async (err) => {

  console.log("Backend error:", err);

  if (err.status === 409) {

    if (err.error?.detail === "Employee ID already exists") {
      this.empIdExistsError = "Employee ID already exists";
    }

    if (err.error?.detail === "Email already exists") {
      this.emailExistsError = "Email already exists";
    }

    if (auth.currentUser) {
      await auth.currentUser.delete();
    }

  } else {
    this.empIdExistsError = "Registration failed";
  }

  this.cd.detectChanges();
}
});
} catch (error: any) {

  console.log("Firebase error:", error);

  if (error.code === 'auth/email-already-in-use') {
    this.emailExistsError = "Email already exists";
    this.emailTouched = true;
    this.cd.detectChanges();
  }

  else if (error.code === 'auth/weak-password') {
    this.emailExistsError = "Password must be at least 6 characters";
    this.passwordTouched = true;
  }

  else if (error.code === 'auth/invalid-email') {
    this.emailExistsError = "Invalid email format";
    this.emailTouched = true;
  }

  else {
    this.emailExistsError = "Signup failed";
  }

}
}
}