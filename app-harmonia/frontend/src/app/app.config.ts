import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { AuthRepository } from './domain/auth/repositories/auth.repository';
import { AuthHttpRepository } from './infrastructure/http/auth.http.repository';
import { ChatRepository } from './domain/chat/repositories/chat.repository';
import { ChatHttpRepository } from './infrastructure/http/chat.http.repository';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(),
    { provide: AuthRepository, useClass: AuthHttpRepository },
    { provide: ChatRepository, useClass: ChatHttpRepository },
  ]
};
