import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';
import { AuthRepository } from '../../domain/auth/repositories/auth.repository';
import { Credentials } from '../../domain/auth/models/credentials.model';
import { User } from '../../domain/auth/models/user.model';
import { environment } from '../../../environments/environment';
import { UUID7 as uuid7 } from 'uuid7-typed';

interface UserApiResponse {
  user_fullname: string;
  user_email: string;
  user_profile: number;
  user_uuidv7: uuid7;
}

@Injectable({
  providedIn: 'root'
})
export class AuthHttpRepository extends AuthRepository {
  private readonly http = inject(HttpClient);

  login(credentials: Credentials): Observable<User> {
    return this.http.post<UserApiResponse>(`${environment.apiUrl}/auth/login`, {
      user_email: credentials.email,
      user_password: credentials.password
    }, { withCredentials: true }).pipe(
      map((response) => ({
        fullname: response.user_fullname,
        email: response.user_email,
        profile: response.user_profile,
        userUuid7: response.user_uuidv7
      }))
    );
  }

  logout(userUuid7: uuid7): Observable<void> {
    return this.http.post<void>(`${environment.apiUrl}/auth/logout/${userUuid7}`, {}, { withCredentials: true });
  }
}
