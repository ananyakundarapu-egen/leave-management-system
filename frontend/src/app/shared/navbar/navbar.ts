import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth';
import { signOut } from "firebase/auth";
import { auth } from '../../services/firebase';
import { Router } from '@angular/router';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class Navbar implements OnInit {

  username: string | null = null;
  role: string | null = null;

  constructor(private authService: AuthService, private router: Router) {}

  ngOnInit() {
    this.authService.username$.subscribe(name => {
      this.username = name;
    });

    this.authService.role$.subscribe(role => {
      this.role = role;
    });
  }

  isLoggedIn() {
    return !!this.username;
  }

  logout() {
    signOut(auth).then(() => {
      this.authService.logout();
      this.router.navigate(['/login']);
    });
  }
}