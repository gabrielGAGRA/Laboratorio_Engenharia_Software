import { describe, it, expect, beforeEach } from 'vitest';
import { AppComponent } from './app.component';
import { RibbitStateService } from './core/ribbit-state.service';
import { AudioPlayerService } from './core/audio-player.service';

describe('AppComponent', () => {
  let component: AppComponent;
  let state: RibbitStateService;
  let player: AudioPlayerService;

  beforeEach(() => {
    localStorage.clear();
    state = new RibbitStateService();
    player = new AudioPlayerService();
    component = new AppComponent(state, player);
  });

  it('should initialize with discover page and app view', () => {
    expect(state.activePage()).toBe('discover');
    expect(state.authView()).toBe('app');
  });

  it('should navigate to different pages', () => {
    component.changePage('playlists');
    expect(state.activePage()).toBe('playlists');

    component.changePage('jams');
    expect(state.activePage()).toBe('jams');
  });

  it('should toggle persistent player playback', () => {
    expect(player.isPlaying()).toBe(false);
    component.togglePlayback();
    expect(player.isPlaying()).toBe(true);
  });
});
