import {IUserData} from "../types/IUserData";
import React, {useState} from "react";

import BellLogo from "assets/bell.svg";
import RingingBellLogo from "assets/bell-ringing.svg";

export interface IProps {
  user: IUserData;
}

export const NotificationBell = ({ user }: IProps) => {
  const [receivedNotification, setReceivedNotification] = useState(true);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(1);

  const clickBellIcon = async () => {
    // TODO
    console.log("Click bell icon");
  };

  return (
    <span onClick={clickBellIcon}>
      <img
        src={receivedNotification ? RingingBellLogo : BellLogo}
        alt={'Bell icon'}
        title={'View notifications'}
      />
      {unreadNotificationCount === 0 ? "" : <span>{unreadNotificationCount}</span>}
    </span>
  );
};

export default NotificationBell;
