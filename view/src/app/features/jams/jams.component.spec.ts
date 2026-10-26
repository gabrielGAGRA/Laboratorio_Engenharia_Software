import { describe, it, expect, beforeEach } from 'vitest';
import { JamsComponent } from './jams.component';
import { RibbitStateService } from '../../core/ribbit-state.service';

describe('JamsComponent', () => {
  let component: JamsComponent;
  let state: RibbitStateService;

  beforeEach(() => {
    localStorage.clear();
    state = new RibbitStateService();
    component = new JamsComponent(state);
  });

  it('should join jam room when submitting code', () => {
    expect(state.jamState().active).toBe(false);
    component.joinJam('RIBBIT-123');
    expect(state.jamState().active).toBe(true);
  });

  it('should vote to skip current track', () => {
    state.setJamActive(true);
    expect(state.jamVotes()).toBe(0);
    component.voteSkip();
    expect(state.jamVotes()).toBe(1);
  });

  it('should allow copying room code', () => {
    component.copyCode();
    expect(state.toast()).toContain('copiado');
  });
});
