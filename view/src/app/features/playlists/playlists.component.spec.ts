import { describe, it, expect, beforeEach } from 'vitest';
import { PlaylistsComponent } from './playlists.component';
import { RibbitStateService } from '../../core/ribbit-state.service';
import { AudioPlayerService } from '../../core/audio-player.service';

describe('PlaylistsComponent', () => {
  let component: PlaylistsComponent;
  let state: RibbitStateService;
  let player: AudioPlayerService;

  beforeEach(() => {
    localStorage.clear();
    state = new RibbitStateService();
    player = new AudioPlayerService();
    component = new PlaylistsComponent(state, player);
  });

  it('should switch between playlists and queue tabs', () => {
    expect(component.currentTab()).toBe('playlists');
    component.selectTab('queue');
    expect(component.currentTab()).toBe('queue');
  });

  it('should add song to queue when approving', () => {
    component.selectTab('queue');
    component.decideQueue(true);
    expect(state.queue().length).toBe(1);
  });

  it('should trigger modal to create playlist or save queue', () => {
    component.openCreateModal();
    expect(state.activeModal()).toBe('playlist');

    component.openSaveQueueModal();
    expect(state.activeModal()).toBe('save-queue');
  });
});
