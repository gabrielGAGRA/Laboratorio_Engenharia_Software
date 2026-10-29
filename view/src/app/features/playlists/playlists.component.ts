import {
  Component,
  ChangeDetectionStrategy,
  inject,
  signal,
  computed,
} from '@angular/core';
import { RibbitStateService } from '../../core/ribbit-state.service';
import { PlaylistService } from '../../core/services/playlist.service';
import { SongService } from '../../core/services/song.service';
import { safeInject } from '../../core/safe-inject';
import { AudioPlayerService } from '../../core/audio-player.service';
import { IconComponent } from '../../shared/icon.component';
import { Playlist, Song } from '@ribbit/shared-types';

@Component({
  selector: 'app-playlists',
  standalone: true,
  imports: [IconComponent],
  templateUrl: './playlists.component.html',
  styleUrl: './playlists.component.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class PlaylistsComponent {
  protected readonly playlistService: PlaylistService = safeInject(PlaylistService, new PlaylistService());
  protected readonly songService: SongService = safeInject(SongService, new SongService());

  protected readonly oceanImg =
    'https://images.unsplash.com/photo-1505142468610-359e7d316be0?auto=format&fit=crop&w=1000&q=85';
  protected readonly palmImg =
    'https://images.unsplash.com/photo-1535392432937-a27c36ec07b5?auto=format&fit=crop&w=700&q=85';

  readonly currentTab = signal<'playlists' | 'queue'>('playlists');
  protected readonly queueDrag = signal<number>(0);
  private queuePointerStart: number | null = null;

  readonly currentQueueSong = computed<Song>(() => {
    const songs = this.state.songs();
    const cursor = this.state.queueCursor();
    return songs[cursor % songs.length];
  });

  readonly lastQueuePreview = computed<readonly number[]>(() => {
    return this.state.lastQueue().slice(0, 3);
  });

  readonly queueCardTransform = computed<string | undefined>(() => {
    const drag = this.queueDrag();
    if (drag === 0) return undefined;
    return `translateX(${drag}px) rotate(${drag / 30}deg)`;
  });

  constructor(
    protected readonly state: RibbitStateService = inject(RibbitStateService),
    protected readonly player: AudioPlayerService = inject(AudioPlayerService),
  ) {}

  selectTab(tab: 'playlists' | 'queue'): void {
    this.currentTab.set(tab);
  }

  decideQueue(add: boolean): void {
    this.state.decideQueue(add);
    this.queueDrag.set(0);
  }

  getSong(index: number): Song {
    const list = this.state.songs();
    return list[index % list.length];
  }

  playQueue(): void {
    this.player.play();
    this.state.notify('Reproduzindo sua fila temporária.');
  }

  openCreateModal(): void {
    this.state.setModal('playlist');
  }

  openSaveQueueModal(): void {
    this.state.setModal('save-queue');
  }

  openPlaylistView(name: string): void {
    this.state.setModal(`playlist-view:${name}`);
  }

  onQueuePointerDown(event: PointerEvent): void {
    this.queuePointerStart = event.clientX;
    (event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
  }

  onQueuePointerMove(event: PointerEvent): void {
    if (this.queuePointerStart !== null) {
      this.queueDrag.set(event.clientX - this.queuePointerStart);
    }
  }

  onQueuePointerCancel(): void {
    this.queuePointerStart = null;
    this.queueDrag.set(0);
  }

  onQueuePointerUp(): void {
    if (this.queuePointerStart === null) return;
    this.queuePointerStart = null;
    const drag = this.queueDrag();
    if (drag > 65) {
      this.decideQueue(true);
    } else if (drag < -65) {
      this.decideQueue(false);
    } else {
      this.queueDrag.set(0);
    }
  }
}
