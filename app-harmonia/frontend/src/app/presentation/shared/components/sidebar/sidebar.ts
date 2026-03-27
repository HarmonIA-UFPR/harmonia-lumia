import { Component, ChangeDetectionStrategy, inject, signal, computed } from '@angular/core';
import { ChatService } from '../../../../application/chat/chat.service';
import { AuthService } from '../../../../application/auth/auth.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class Sidebar {
  private readonly chatService = inject(ChatService);
  private readonly authService = inject(AuthService);

  readonly chats = this.chatService.chats;
  readonly selectedChatUuid = this.chatService.selectedChatUuid;
  readonly isLoading = this.chatService.isLoading;

  readonly isMenuOpen = signal(false);

  readonly currentUser = this.authService.currentUser;
  
  readonly firstName = computed(() => {
    const user = this.currentUser();
    if (!user || !user.fullname) return '';
    const names = user.fullname.split(' ');
    return names.length > 0 ? names[0] : '';
  });

  readonly userInitial = computed(() => {
    const fName = this.firstName();
    return fName ? fName.charAt(0).toUpperCase() : 'U';
  });

  toggleMenu() {
    this.isMenuOpen.update(v => !v);
  }

  newChat() {
    this.chatService.createNewChat();
    this.isMenuOpen.set(false);
  }

  logout() {
    this.authService.logout();
    this.isMenuOpen.set(false);
  }

  selectChat(chatUuid7: any) {
    this.chatService.selectChat(chatUuid7);
  }
}
