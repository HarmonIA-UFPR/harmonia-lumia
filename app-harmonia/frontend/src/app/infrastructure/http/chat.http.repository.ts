import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpResponse } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map } from 'rxjs/operators';
import { ChatRepository } from '../../domain/chat/repositories/chat.repository';
import { Chat } from '../../domain/chat/models/chat.model';
import { Message } from '../../domain/chat/models/message.model';
import { HistoryChat, HistoryChatResponse, CreateHistoryChatRequest } from '../../domain/chat/models/history-chat.model';
import { environment } from '../../../environments/environment';
import { UUID7 as uuid7 } from 'uuid7-typed';

@Injectable({
  providedIn: 'root'
})
export class ChatHttpRepository extends ChatRepository {
  private readonly http = inject(HttpClient);

  getChats(): Observable<Chat[]> {
    // Mantido para compatibilidade — uso real via getSessionsByUser + mapeamento no service
    return of([]);
  }

  getMessages(chatUuid7: uuid7): Observable<Message[]> {
    // TODO: Substituir por chamada real quando o backend estiver pronto
    // return this.http.get<Message[]>(`${environment.apiUrl}/chats/${chatUuid7}/messages`);
    return of([
      {
        uuid7: 'msg-1' as unknown as uuid7,
        chatUuid7: chatUuid7,
        content: 'Olá! Sou o HarmonIA, seu assistente inteligente e amigável. Como posso ajudá-lo hoje?',
        sender: 'assistant' as const,
        timestamp: new Date()
      }
    ]);
  }

  getSessionsByUser(userUuid7: uuid7): Observable<string[]> {
    return this.http.get<string[]>(
      `${environment.apiAgentUrl}/history-chats/by-user/${userUuid7}`
    );
  }

  getHistoryChats(sessionUuid7: uuid7): Observable<HistoryChatResponse> {
    return this.http.get<HistoryChatResponse>(
      `${environment.apiAgentUrl}/history-chats/by-session/${sessionUuid7}`
    );
  }

  createHistoryChat(request: CreateHistoryChatRequest): Observable<HistoryChat> {
    return this.http.post<HistoryChat>(
      `${environment.apiAgentUrl}/history-chats`,
      request,
      { observe: 'response' }
    ).pipe(
      map((response: HttpResponse<HistoryChat>) => {
        if (response.status === 201 && response.body) {
          return response.body;
        }
        throw new Error(`Expected HTTP 201 Created, but got ${response.status}`);
      })
    );
  }
}
