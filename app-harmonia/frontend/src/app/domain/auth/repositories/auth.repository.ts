import { Observable } from 'rxjs';
import { Credentials } from '../models/credentials.model';
import { User } from '../models/user.model';
import { UUID7 as uuid7 } from 'uuid7-typed';

export abstract class AuthRepository {
  abstract login(credentials: Credentials): Observable<User>;
  abstract logout(userUuid7: uuid7): Observable<void>;
}
