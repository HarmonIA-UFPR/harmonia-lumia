import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Chat } from './chat';

import { ChatService } from '../../../application/chat/chat.service';
import { ChatRepository } from '../../../domain/chat/repositories/chat.repository';
import { AuthService } from '../../../application/auth/auth.service';
import { of } from 'rxjs';

describe('Chat', () => {
  let component: Chat;
  let fixture: ComponentFixture<Chat>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Chat],
      providers: [
        ChatService,
        { provide: ChatRepository, useValue: { getSessionsByUser: () => of([]) } },
        { provide: AuthService, useValue: { currentUser: () => ({ id: '123' }) } }
      ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Chat);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
