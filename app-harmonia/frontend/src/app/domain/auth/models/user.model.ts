import { UUID7 as uuid7 } from 'uuid7-typed';

export interface User {
  fullname: string;
  email: string;
  profile: number;
  userUuid7: uuid7;
}
