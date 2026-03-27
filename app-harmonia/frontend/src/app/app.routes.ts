import { Routes } from '@angular/router';
import { Home } from './presentation/pages/home/home';
import { authGuard } from './domain/auth/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    component: Home
  },
  {
    path: 'auth/login',
    loadComponent: () => import('./presentation/pages/auth/login/login').then(m => m.Login),
  },
  {
    path: 'chat',
    loadComponent: () => import('./presentation/pages/chat/chat').then(m => m.Chat),
    canActivate: [authGuard]
  },
  {
    path: 'cards',
    loadComponent: () => import('./presentation/shared/components/tool-card/tool-card').then(m => m.ToolCard),
  },
  { path: '**', redirectTo: '' }
];
