export type IconName =
  | 'pond'
  | 'music'
  | 'users'
  | 'search'
  | 'user'
  | 'arrow'
  | 'chevron'
  | 'heart'
  | 'star'
  | 'close'
  | 'undo'
  | 'play'
  | 'pause'
  | 'filter'
  | 'bell'
  | 'plus'
  | 'clock'
  | 'headphones'
  | 'settings'
  | 'logout'
  | 'sparkles'
  | 'volume'
  | 'check'
  | 'send'
  | 'globe'
  | 'repeat';

export type DecisionKind = 'like' | 'love' | 'reject';

export interface Decision {
  readonly index: number;
  readonly kind: DecisionKind;
}

export interface Song {
  readonly title: string;
  readonly artist: string;
  readonly genre: string;
  readonly time: string;
  readonly image: string;
  readonly album: string;
  readonly year: string;
  readonly match: number;
}

export interface CommunityReview {
  readonly id: number;
  readonly author: string;
  readonly initials: string;
  readonly text: string;
  readonly likes: number;
  readonly age: string;
  readonly date: number;
}

export interface Playlist {
  readonly name: string;
  readonly count: number;
  readonly duration: string;
}

export interface NavigationItem {
  readonly id: string;
  readonly label: string;
  readonly sub: string;
  readonly icon: IconName;
}

export interface SubscriptionPlan {
  readonly name: string;
  readonly displayName: string;
  readonly price: string;
  readonly copy: string;
  readonly features: readonly string[];
  readonly featured?: boolean;
}

export interface JamState {
  readonly active: boolean;
  readonly code: string;
  readonly roomName: string;
  readonly votes: number;
  readonly voteThreshold: number;
  readonly durationHours: number;
  readonly durationMinutes: number;
}

export interface MetricItem {
  readonly value: string;
  readonly label: string;
  readonly detail: string;
  readonly icon: IconName;
}

export interface RankedArtist {
  readonly song: Song;
  readonly rank: string;
  readonly time: string;
}

export interface RankedGenre {
  readonly genre: string;
  readonly percentage: number;
  readonly rank: string;
}
