import { Component, ChangeDetectionStrategy, input } from '@angular/core';
import { HistoryChat } from '../../../../domain/chat/models/history-chat.model';
import { ToolCard } from '../tool-card/tool-card';
import { NgFor, NgIf } from '@angular/common';

@Component({
  selector: 'app-history-card',
  standalone: true,
  imports: [ToolCard, NgFor, NgIf],
  templateUrl: './history-card.html',
  styleUrls: ['./history-card.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class HistoryCard {
  historyChat = input.required<HistoryChat>();
}
