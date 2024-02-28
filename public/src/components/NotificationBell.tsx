import {IUserData} from "../types/IUserData";
import React, {useState} from "react";

import BellLogo from "assets/bell.svg";
import RingingBellLogo from "assets/bell-ringing.svg";

interface IProps {
  user: IUserData;
  onClick: () => void;
}

export const NotificationBell = ({ onClick }: IProps) => {
  const [receivedNotification, setReceivedNotification] = useState(true);
  const [unreadNotificationCount, setUnreadNotificationCount] = useState(1);

  return (
    <span onClick={onClick}>
      <img
        src={receivedNotification ? RingingBellLogo : BellLogo}
        alt={'Bell icon'}
        className={'icon'}
        title={'View notifications'}
      />
      {unreadNotificationCount === 0 ? "" : <span>{unreadNotificationCount}</span>}
    </span>
  );
};

export default NotificationBell;
