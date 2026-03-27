import { Component, ChangeDetectionStrategy, inject, signal, ElementRef, viewChild, OnInit } from '@angular/core';
import { FormControl, ReactiveFormsModule,AbstractControl, ValidationErrors } from '@angular/forms';
import { Sidebar } from '../../shared/components/sidebar/sidebar';
import { ChatService } from '../../../application/chat/chat.service';
import { Message } from '../../../domain/chat/models/message.model';
import { SlicePipe } from '@angular/common';
import { ToolCard } from '../../shared/components/tool-card/tool-card';
import { HistoryCard } from '../../shared/components/history-card/history-card';
import { UUID7 as uuid7 } from 'uuid7-typed';
import { uuidv7 } from 'uuidv7';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [Sidebar, ReactiveFormsModule, SlicePipe, ToolCard, HistoryCard],
  templateUrl: './chat.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class Chat implements OnInit {
  readonly tool_uuidv7: uuid7 = '019c7b2c-0d12-7360-b03a-3183fb29dc5b' as unknown as uuid7;
  private readonly chatService = inject(ChatService);

  readonly selectedChat = this.chatService.selectedChat;
  readonly historyChats = this.chatService.historyChats;
  readonly isHistoryLoading = this.chatService.isHistoryLoading;

  readonly messages = signal<Message[]>([
    {
      uuid7: 'msg-1' as unknown as uuid7,
      chatUuid7: 'any' as unknown as uuid7,
      content: 'Olá! Sou o HarmonIA, seu assistente inteligente e amigável. Como posso ajudá-lo hoje?',
      sender: 'useless',
      timestamp: new Date()
    }
  ]);

  readonly promptControl = new FormControl('', { nonNullable: true });
  readonly isTyping = signal(false);

  private readonly messagesContainer = viewChild<ElementRef<HTMLDivElement>>('messagesContainer');

  ngOnInit(): void {
    this.chatService.loadChats();
  }

  sendMessage() {
    const content = this.promptControl.value?.trim();
    if (!content) return;

    this.promptControl.reset();
    const currentChat = this.selectedChat();
    const chatUuid7 = (currentChat ? currentChat.chatUuid7 : 'default') as unknown as uuid7;

    this.isTyping.set(true);
    // Para feedback visual inicial, podemos rolar para o bottom.
    this.scrollToBottom();
    
    // Chama a API real, que internamente já faz o POST, verifica o HTTP 201 e adiciona o history-card recebido
    this.chatService.sendPrompt(chatUuid7, content).subscribe({
      next: (response) => {
        this.isTyping.set(false);
        this.scrollToBottom();
      },
      error: (err) => {
        console.error('Erro ao enviar mensagem:', err);
        this.isTyping.set(false);
        this.messages.update(msgs => [...msgs, {
          uuid7: uuidv7() as uuid7,
          chatUuid7: chatUuid7,
          content: `Erro ao comunicar com a API: ${err.message}`,
          sender: 'assistant',
          timestamp: new Date()
        }]);
        this.scrollToBottom();
      }
    });
  }

  private scrollToBottom() {
    setTimeout(() => {
      const container = this.messagesContainer();
      if (container?.nativeElement) {
        container.nativeElement.scrollTop = container.nativeElement.scrollHeight;
      }
    }, 50);
  }

  //TOOL PARA TESTAR TOOLCARD
  tool= [
     {
      id: 1,
      nome: 'Ferramenta 1',
      descricao: 'Gerador de textos automáticos',
      link_oficial: '#',
      link_git: '',
      link_doc: ''
    },
  ]

}
