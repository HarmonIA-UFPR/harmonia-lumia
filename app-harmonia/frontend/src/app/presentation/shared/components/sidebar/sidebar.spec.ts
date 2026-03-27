import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Sidebar } from './sidebar';

import { ChatService } from '../../../../application/chat/chat.service';
import { AuthService } from '../../../../application/auth/auth.service';
import { ChatRepository } from '../../../../domain/chat/repositories/chat.repository';
import { AuthRepository } from '../../../../domain/auth/repositories/auth.repository';
import { of } from 'rxjs';

describe('Sidebar', () => {
  let component: Sidebar;
  let fixture: ComponentFixture<Sidebar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Sidebar],
      providers: [
        ChatService,
        AuthService,
        { provide: ChatRepository, useValue: { getSessionsByUser: () => of([]) } },
        { provide: AuthRepository, useValue: { login: () => of() } }
      ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Sidebar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
