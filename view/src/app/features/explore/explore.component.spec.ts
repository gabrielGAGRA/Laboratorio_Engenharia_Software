import { describe, it, expect, beforeEach } from 'vitest';
import { ExploreComponent } from './explore.component';
import { RibbitStateService } from '../../core/ribbit-state.service';

describe('ExploreComponent', () => {
  let component: ExploreComponent;
  let state: RibbitStateService;

  beforeEach(() => {
    localStorage.clear();
    state = new RibbitStateService();
    component = new ExploreComponent(state);
  });

  it('should filter songs based on search query', () => {
    component.query.set('Bloom');
    expect(component.filteredSongs().length).toBe(1);
    expect(component.filteredSongs()[0].title).toBe('Bloom');

    component.query.set('Inexistente123');
    expect(component.filteredSongs().length).toBe(0);
  });

  it('should toggle history expansion', () => {
    expect(component.historyExpanded()).toBe(false);
    component.toggleHistory();
    expect(component.historyExpanded()).toBe(true);
  });

  it('should toggle review likes and sort reviews', () => {
    const reviewId = 1;
    expect(component.reviewLikes()[reviewId]).toBeFalsy();
    component.toggleReviewLike(reviewId);
    expect(component.reviewLikes()[reviewId]).toBe(true);

    component.reviewSort.set('likes');
    const sorted = component.sortedReviews();
    expect(sorted[0].id).toBe(reviewId);
  });
});
