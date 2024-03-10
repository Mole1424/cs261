/**
 * Type of the notification.
 * 1 - company;
 * 2 - article;
 */
type NotificationType = 1 | 2;

export interface INotification {
  id: number;
  targetId: number;
  targetType: NotificationType;
  message: string;
  read: boolean;
  received: string; // Datetime
}

export default INotification;

export interface INotificationStats {
  total: number;
  unread: number;
}
