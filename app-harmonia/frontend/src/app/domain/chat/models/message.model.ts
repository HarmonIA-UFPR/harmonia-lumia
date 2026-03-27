import { UUID7 as uuid7 } from 'uuid7-typed';

export interface Message {
  uuid7: uuid7;
  chatUuid7: uuid7;
  content: string;
  sender: 'user' | 'assistant' | 'useless';
  timestamp: Date;
}
