import { Injectable, inject, signal, computed } from '@angular/core';
import { AuthRepository } from '../../domain/auth/repositories/auth.repository';
import { SessionStorage } from '../../infrastructure/storage/session.storage';
import { Credentials } from '../../domain/auth/models/credentials.model';
import { User } from '../../domain/auth/models/user.model';
import { Router } from '@angular/router';
import { catchError, tap } from 'rxjs/operators';
import { throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly authRepo = inject(AuthRepository);
  private readonly sessionStorage = inject(SessionStorage);
  private readonly router = inject(Router);

  private readonly userSignal = signal<User | null>(this.sessionStorage.getUser());

  readonly currentUser = this.userSignal.asReadonly();
  readonly isAuthenticated = computed(() => this.currentUser() !== null);

  login(credentials: Credentials) {
    return this.authRepo.login(credentials).pipe(
      tap((user) => {
        this.sessionStorage.setUser(user);
        this.userSignal.set(user);
        this.router.navigate(['/chat']);
      }),
      catchError((error) => {
        return throwError(() => error);
      })
    );
  }

  logout(): void {
    const user = this.currentUser();
    if (!user) {
      this.sessionStorage.clear();
      this.userSignal.set(null);
      this.router.navigate(['/']);
      return;
    }

    this.authRepo.logout(user.userUuid7).subscribe({
      next: () => {
        this.sessionStorage.clear();
        this.userSignal.set(null);
        this.router.navigate(['/']);
      },
      error: () => {
        this.sessionStorage.clear();
        this.userSignal.set(null);
        this.router.navigate(['/']);
      }
    });
  }
}
