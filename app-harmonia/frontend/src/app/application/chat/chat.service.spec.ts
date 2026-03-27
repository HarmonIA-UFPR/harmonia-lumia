import { TestBed } from '@angular/core/testing';
import { ChatService } from './chat.service';
import { ChatRepository } from '../../domain/chat/repositories/chat.repository';
import { AuthService } from '../auth/auth.service';
import { of } from 'rxjs';

describe('ChatService', () => {
  let service: ChatService;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        {
          provide: ChatRepository,
          useValue: {
            getChats: () => of([]),
            getMessages: () => of([]),
            getSessionsByUser: () => of([])
          }
        },
        {
          provide: AuthService,
          useValue: {
            currentUser: () => ({ id: '123' }),
            isAuthenticated: () => true
          }
        }
      ]
    });
    service = TestBed.inject(ChatService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
