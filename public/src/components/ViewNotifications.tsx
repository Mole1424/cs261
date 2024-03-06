import IViewProps from "../types/IViewProps";
import {useEffect, useState} from "react";
import INotification, {INotificationStats} from "../types/INotification";
import axios, {AxiosResponse} from "axios";
import {formatDateTime} from "../util";

import "styles/view-cards.scss";
import "styles/view-notifications.scss";
import {headerFormData} from "../constants";

export const ViewNotifications = ({ }: IViewProps) => {
  const [notifications, setNotifications] = useState<INotification[]>([]);

  // Fetch and populate notification list
  useEffect(() => void requestNotifications()
    .then(response => response && setNotifications(response)), []);

  /** Click on the provided notification. */
  const clickNotification = (notification: INotification) => {
    void requestMarkAsRead(notification.id);
    notification.read = true;
    setNotifications([...notifications]);

    switch (notification.targetType) {
      case 1: // company
        open(`${location.origin}/#company/${notification.targetId}`);
        break;
      case 2: // article
        open(`${location.origin}/#article/${notification.targetId}`);
        break;
    }
  };

  return (
    <main className={'content-notifications content-cards'}>
      {notifications.length === 0
        ? <em>You have no notifications.</em>
        : (
        <div className={'cards'}>
          {notifications.map(notification =>
            <div
              key={notification.id}
              className={'notification'}
              data-id={notification.id}
              data-read={notification.read}
              onClick={() => clickNotification(notification)}
            >
              <span className={'notification-received'}>Received {formatDateTime(new Date(notification.received))}</span>
              <span className={'notification-message'}>{notification.message}</span>
            </div>
          )}
        </div>
        )}
    </main>
  );
};

export default ViewNotifications;

/**
 * Attempt to fetch notifications.
 */
export async function requestNotifications() {
  try {
    const response = await axios.get('/user/notifications') as AxiosResponse<INotification[], unknown>;
    return response.data;
  } catch {
    return null;
  }
}

/**
 * Mark a user's notifications as read, return success.
 */
export async function requestMarkAsRead(id: number) {
  try {
    const response = await axios.post('/notification/mark-as-read', { id }, headerFormData) as AxiosResponse<{
      error: boolean;
      message?: string;
    }, never>;
    return !response.data.error;
  } catch {
    return false;
  }
}

/**
 * Mark all user's notifications as read, return success.
 */
export async function requestMarkAllAsRead() {
  try {
    await axios.post('/notification/read-all', {}, headerFormData);
    return true;
  } catch {
    return false;
  }
}

/**
 * Request notification statistics.
 */
export async function requestNotificationStats() {
  try {
    const response = await axios.get('/user/notification-stats') as AxiosResponse<INotificationStats, unknown>;
    return response.data;
  } catch {
    return null;
  }
}
