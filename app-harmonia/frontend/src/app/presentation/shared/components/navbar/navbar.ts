import { Component, inject, ChangeDetectionStrategy } from '@angular/core';
import { AuthService } from '../../../../application/auth/auth.service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-navbar',
  imports: [
    RouterLink
  ],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class Navbar {
  private readonly authService = inject(AuthService);
  readonly isAuthenticated = this.authService.isAuthenticated;

  logout() {
    this.authService.logout();
  }

}
