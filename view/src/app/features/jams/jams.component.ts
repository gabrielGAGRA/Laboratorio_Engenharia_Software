import {
  Component,
  ChangeDetectionStrategy,
  inject,
  computed,
} from '@angular/core';
import { Router } from '@angular/router';
import { RibbitStateService } from '../../core/ribbit-state.service';
import { SongService } from '../../core/services/song.service';
import { safeInject } from '../../core/safe-inject';
import { IconComponent } from '../../shared/icon.component';
import { Song } from '@ribbit/shared-types';

@Component({
  selector: 'app-jams',
  standalone: true,
  imports: [IconComponent],
  templateUrl: './jams.component.html',
  styleUrl: './jams.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JamsComponent {
  private readonly router: Router | null = safeInject(Router, null);
  protected readonly songService: SongService = safeInject(SongService, new SongService());

  readonly currentSong = computed<Song>(() => this.state.currentSong());

  readonly upcomingSongs = computed<readonly Song[]>(() => {
    return this.state.songs().slice(1, 4);
  });

  readonly formattedDurationMinutes = computed<string>(() => {
    return String(this.state.jamState().durationMinutes).padStart(2, '0');
  });

  constructor(
    protected readonly state: RibbitStateService = inject(RibbitStateService),
  ) {}

  openJamModal(): void {
    this.state.setModal('jam');
  }

  joinJam(code: string): void {
    this.state.setJamActive(true);
    this.state.notify(`Você entrou na Jam de demonstração (${code}).`);
  }

  onJoinSubmit(event: Event): void {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const input = form.elements.namedItem('jamCode') as HTMLInputElement;
    this.joinJam(input.value || 'RIBBIT-729');
  }

  copyCode(): void {
    const code = this.state.jamState().code;
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(code);
    }
    this.state.notify(`Código ${code} copiado.`);
  }

  voteSkip(): void {
    this.state.voteSkipJam();
  }

  likeCurrent(): void {
    this.state.decide('like');
  }

  loveTrack(song: Song): void {
    const songIndex = this.state.songs().indexOf(song);
    if (songIndex >= 0) {
      const hist = [
        ...this.state.history().filter((item) => item.index !== songIndex),
        { index: songIndex, kind: 'love' as const },
      ];
      this.state.history.set(hist);
      this.state.notify(`${song.title} foi adicionada às suas favoritas.`);
    }
  }

  goToDiscover(): void {
    this.state.setPage('discover');
    void this.router?.navigate(['/discover']);
    this.state.notify('Dê likes para ajudar a construir a fila da Jam.');
  }
}
