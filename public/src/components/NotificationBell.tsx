import React, {useEffect, useState} from "react";
import {requestNotificationStats} from "./ViewNotifications";
import {formatNumber} from "../util";

import BellLogo from "assets/bell.svg";
import RingingBellLogo from "assets/bell-ringing.svg";
import IViewProps from "../types/IViewProps";
import {ICbEvent} from "../types/AppEvent";

export const NotificationBell = ({ eventCallback }: IViewProps) => {
  const [receivedNotification, setReceivedNotification] = useState(false);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(0);

  /** Logic loop. */
  const updateDetails = async () => {
    const stats = await requestNotificationStats();

    if (stats) {
      // New unread notification?
      if (stats.unread !== unreadNotificationCount) {
        setUnreadNotificationCount(stats.unread);
        setReceivedNotification(true);
      }
    }
  };

  /** Click on bell. */
  const onClick = () => {
    setReceivedNotification(false);

    eventCallback({
      type: 'load-notifications'
    } as ICbEvent);
  };

  useEffect(() => {
    void updateDetails();

    const intervalId = setInterval(updateDetails, 30_000);

    return () => clearInterval(intervalId);
  }, []);

  return (
    <span className={'bell-container'} data-received={receivedNotification} onClick={onClick}>
      <img
        src={receivedNotification ? RingingBellLogo : BellLogo}
        alt={'Bell icon'}
        className={'icon'}
        title={'View notifications'}
      />
      {unreadNotificationCount === 0 ? "" : <span>{formatNumber(unreadNotificationCount)}</span>}
    </span>
  );
};

export default NotificationBell;
