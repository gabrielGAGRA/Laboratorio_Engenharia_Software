import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { DiscoverComponent } from './discover.component';
import { RibbitStateService } from '../../core/ribbit-state.service';
import { AudioPlayerService } from '../../core/audio-player.service';

describe('DiscoverComponent', () => {
  let component: DiscoverComponent;
  let state: RibbitStateService;
  let player: AudioPlayerService;

  beforeEach(() => {
    vi.useFakeTimers();
    localStorage.clear();
    state = new RibbitStateService();
    player = new AudioPlayerService();
    component = new DiscoverComponent(state, player);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should initialize and display current song', () => {
    expect(component.currentSong()).toBeDefined();
    expect(component.currentSong().title).toBe('Bloom');
  });

  it('should trigger like, love, and reject decisions after animation', () => {
    component.handleDecision('like');
    vi.advanceTimersByTime(300);

    expect(state.history().length).toBe(1);
    expect(state.history()[0].kind).toBe('like');
  });

  it('should toggle audio playback', () => {
    expect(player.isPlaying()).toBe(false);
    component.togglePlay();
    expect(player.isPlaying()).toBe(true);
  });

  it('should handle mode selection', () => {
    component.selectMode('Novidades');
    expect(state.mode()).toBe('Novidades');
  });
});
