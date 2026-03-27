import { Injectable, inject, signal, computed } from '@angular/core';
import { ChatRepository } from '../../domain/chat/repositories/chat.repository';
import { AuthService } from '../auth/auth.service';
import { Observable, tap, throwError } from 'rxjs';
import { Chat } from '../../domain/chat/models/chat.model';
import { HistoryChat, CreateHistoryChatRequest } from '../../domain/chat/models/history-chat.model';
import { UUID7 as uuid7 } from 'uuid7-typed';
import { uuidv7 } from 'uuidv7';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private readonly chatRepo = inject(ChatRepository);
  private readonly authService = inject(AuthService);

  private readonly MAX_SESSIONS = 10;

  private readonly chatsSignal = signal<Chat[]>([]);
  private readonly selectedChatUuidSignal = signal<uuid7 | null>(null);
  private readonly isLoadingSignal = signal(false);

  private readonly historyChatsSignal = signal<HistoryChat[]>([]);
  private readonly isHistoryLoadingSignal = signal(false);

  readonly chats = this.chatsSignal.asReadonly();
  readonly selectedChatUuid = this.selectedChatUuidSignal.asReadonly();
  readonly isLoading = this.isLoadingSignal.asReadonly();
  readonly historyChats = this.historyChatsSignal.asReadonly();
  readonly isHistoryLoading = this.isHistoryLoadingSignal.asReadonly();

  readonly selectedChat = computed(() => {
    const chatUuid7 = this.selectedChatUuid();
    if (!chatUuid7) return null;
    return this.chats().find(c => c.chatUuid7 === chatUuid7) || null;
  });

  loadChats(): void {
    const user = this.authService.currentUser();
    console.log('[ChatService] loadChats chamado. User:', user);

    if (!user) {
      console.warn('[ChatService] Usuário não autenticado — abortando loadChats.');
      return;
    }

    console.log('[ChatService] Buscando sessões para userId:', user.userUuid7);
    this.isLoadingSignal.set(true);

    this.chatRepo.getSessionsByUser(user.userUuid7).subscribe({
      next: (sessionIds) => {
        console.log('[ChatService] Sessões recebidas da API:', sessionIds);

        const chats: Chat[] = sessionIds
          .slice(0, this.MAX_SESSIONS)
          .map((uuid, index) => ({
            chatUuid7: uuid as uuid7,
            title: `Chat ${index + 1}`
          }));

        console.log('[ChatService] Chats mapeados:', chats);
        this.chatsSignal.set(chats);
        this.isLoadingSignal.set(false);
      },
      error: (err) => {
        console.error('[ChatService] ERRO ao carregar sessões de chat:', err);
        console.error('[ChatService] Status:', err?.status, '| Mensagem:', err?.message);
        this.chatsSignal.set([]);
        this.isLoadingSignal.set(false);
      }
    });
  }

  selectChat(chatUuid7: uuid7): void {
    this.selectedChatUuidSignal.set(chatUuid7);
    this.loadHistoryChats(chatUuid7);
  }

  loadHistoryChats(sessionUuid7: uuid7): void {
    this.isHistoryLoadingSignal.set(true);
    this.historyChatsSignal.set([]); // Limpa o histórico anterior ao trocar de chat

    this.chatRepo.getHistoryChats(sessionUuid7).subscribe({
      next: (response) => {
        console.log('[ChatService] Histórico de chats recebido:', response);
        this.historyChatsSignal.set(response.history_chats || []);
        this.isHistoryLoadingSignal.set(false);
      },
      error: (err) => {
        console.error('[ChatService] ERRO ao carregar histórico:', err);
        this.historyChatsSignal.set([]);
        this.isHistoryLoadingSignal.set(false);
      }
    });
  }

  createNewChat(): void {
    const newUuid = uuidv7() as uuid7;
    const currentCount = this.chats().length;
    const newChat: Chat = { chatUuid7: newUuid, title: `Chat ${currentCount + 1}` };
    this.chatsSignal.update(chats => [...chats, newChat]);
    this.selectedChatUuidSignal.set(newUuid);
  }

  sendPrompt(sessionUuid7: uuid7, prompt: string): Observable<HistoryChat> {
    const user = this.authService.currentUser();
    
    if (!user) {
      console.warn('[ChatService] Usuário não autenticado — abortando sendPrompt.');
      return throwError(() => new Error('Usuário não autenticado'));
    }

    const request: CreateHistoryChatRequest = {
      his_session_uuidv7: sessionUuid7,
      user_profile: user.profile || 1,
      user_prompt: prompt,
      user_uuid: user.userUuid7
    };

    return this.chatRepo.createHistoryChat(request).pipe(
      tap((newChat) => {
        // Atualiza o signal de histórico com a nova mensagem assim que for retornada com sucesso
        this.historyChatsSignal.update(chats => [...chats, newChat]);
      })
    );
  }
}
