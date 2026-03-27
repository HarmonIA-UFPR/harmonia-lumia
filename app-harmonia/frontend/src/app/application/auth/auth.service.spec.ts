import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';
import { AuthRepository } from '../../domain/auth/repositories/auth.repository';
import { of } from 'rxjs';

describe('AuthService', () => {
  let service: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        {
          provide: AuthRepository,
          useValue: {
            login: () => of({}),
            logout: () => of(void 0)
          }
        }
      ]
    });
    service = TestBed.inject(AuthService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
