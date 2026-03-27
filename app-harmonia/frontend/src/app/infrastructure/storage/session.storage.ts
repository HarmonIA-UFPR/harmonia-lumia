import { Injectable } from '@angular/core';
import { User } from '../../domain/auth/models/user.model';

@Injectable({
  providedIn: 'root'
})
export class SessionStorage {
  private readonly USER_KEY = 'auth_user';

  setUser(user: User): void {
    sessionStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  getUser(): User | null {
    const userStr = sessionStorage.getItem(this.USER_KEY);
    return userStr ? JSON.parse(userStr) : null;
  }

  clear(): void {
    sessionStorage.removeItem(this.USER_KEY);
  }
}
