import {
  Component,
  ChangeDetectionStrategy,
  inject,
} from '@angular/core';
import { RibbitStateService } from '../../core/ribbit-state.service';
import { FrogComponent } from '../../shared/frog.component';
import { IconComponent } from '../../shared/icon.component';

@Component({
  selector: 'app-auth',
  standalone: true,
  imports: [FrogComponent, IconComponent],
  templateUrl: './auth.component.html',
  styleUrl: './auth.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AuthComponent {
  constructor(
    protected readonly state: RibbitStateService = inject(RibbitStateService),
  ) {}

  protected isRegister(): boolean {
    return this.state.authView() === 'register';
  }

  protected toggleView(): void {
    this.state.setAuthView(this.isRegister() ? 'login' : 'register');
  }

  protected returnToApp(): void {
    this.state.setAuthView('app');
  }

  protected onForgot(): void {
    this.state.notify('Instruções de recuperação enviadas para o seu e-mail.');
  }

  protected onGoogleLogin(): void {
    this.state.notify('Login social disponível apenas na versão integrada.');
  }

  protected onSubmit(event: Event): void {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const nameInput = form.elements.namedItem('name') as HTMLInputElement | null;
    if (this.isRegister() && nameInput?.value) {
      this.state.setUserName(nameInput.value);
    }
    this.state.setAuthView('app');
    this.state.notify(
      this.isRegister()
        ? 'Conta criada. Bem-vindo ao Ribbit!'
        : 'Login realizado em modo demonstrativo.',
    );
  }
}
