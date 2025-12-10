import { User, Resource, Event, Discussion, Message, CommunityGroup, Notification } from '@shared/schema';

// Application state
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  role: string;
  loading: boolean;
}

// Resource query params
export interface ResourceFilters {
  categories: string[];
  distance: string;
  availability: string[];
  search?: string;
  page?: number;
}

// Event related types
export interface CalendarViewType {
  type: 'month' | 'week' | 'day';
  date: Date;
}

// Message related types
export interface MessageThread {
  id: number;
  recipient: User;
  lastMessage: Message;
  unreadCount: number;
}

// Discussion types
export interface DiscussionPost {
  id: number;
  author: User;
  content: string;
  likes: number;
  createdAt: Date;
}

// Form types
export interface LoginFormValues {
  username: string;
  password: string;
}

export interface RegisterFormValues {
  username: string;
  password: string;
  confirmPassword: string;
  email: string;
  role: string;
  firstName: string;
  lastName: string;
}

export interface MessageFormValues {
  recipientId: number;
  subject: string;
  content: string;
}

export interface DiscussionFormValues {
  groupId: number;
  title: string;
  content: string;
}
