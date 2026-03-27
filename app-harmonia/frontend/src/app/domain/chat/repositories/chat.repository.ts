import { Observable } from 'rxjs';
import { Chat } from '../models/chat.model';
import { Message } from '../models/message.model';
import { HistoryChat, HistoryChatResponse, CreateHistoryChatRequest } from '../models/history-chat.model';
import { UUID7 as uuid7 } from 'uuid7-typed';

export abstract class ChatRepository {
  abstract getChats(): Observable<Chat[]>;
  abstract getMessages(chatUuid7: uuid7): Observable<Message[]>;
  abstract getSessionsByUser(userUuid7: uuid7): Observable<string[]>; // Retorna strings por enquanto, depois atualizamos a API se necessário, mas o argumento é uuid7.
  abstract getHistoryChats(sessionUuid7: uuid7): Observable<HistoryChatResponse>;
  abstract createHistoryChat(request: CreateHistoryChatRequest): Observable<HistoryChat>;
}
