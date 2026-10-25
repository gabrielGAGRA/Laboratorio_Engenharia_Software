import { describe, it, expect, beforeEach } from 'vitest';
import { ProfileComponent } from './profile.component';
import { RibbitStateService } from '../../core/ribbit-state.service';
import { AudioPlayerService } from '../../core/audio-player.service';

describe('ProfileComponent', () => {
  let component: ProfileComponent;
  let state: RibbitStateService;
  let player: AudioPlayerService;

  beforeEach(() => {
    localStorage.clear();
    state = new RibbitStateService();
    player = new AudioPlayerService();
    component = new ProfileComponent(state, player);
  });

  it('should switch between like, love, and reject tabs', () => {
    expect(component.selectedTab()).toBe('like');
    component.selectTab('love');
    expect(component.selectedTab()).toBe('love');
  });

  it('should calculate counts for collections', () => {
    expect(component.likeCount()).toBeGreaterThan(0);
    expect(component.loveCount()).toBeGreaterThan(0);
    expect(component.rejectCount()).toBeGreaterThan(0);
  });

  it('should cancel subscription to free plan', () => {
    state.setPlan('Individual');
    expect(state.currentPlan()).toBe('Individual');

    component.cancelSubscription();
    expect(state.currentPlan()).toBe('Free');
    expect(state.toast()).toContain('cancelada');
  });
});
