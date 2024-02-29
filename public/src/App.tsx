import React, {useEffect, useState} from 'react';
import Login, {requestLogout} from "./components/Login";
import {IUserData} from "./types/IUserData";
import {APP_NAME} from "./index";
import TabGroup, {ITab} from "./components/TabGroup";
import ViewFollowing from "./components/ViewFollowing";
import ViewForYou from "./components/ViewForYou";
import ViewRecent from "./components/ViewRecent";
import ViewPopular from "./components/ViewPopular";
import ViewSearch from "./components/ViewSearch";
import UserProfile from "./components/UserProfile";
import NotificationBell from "./components/NotificationBell";
import {ICbEvent, ILoadCompanyEvent, parseStringToEvent} from "./types/AppEvent";
import CompanyDetails from "./components/CompanyDetails";
import Main from "./components/Main";

interface IProps {
  initialUser?: IUserData | null,
  defaultTab?: string; // Label of the default tab
}

export const App = ({ initialUser, defaultTab }: IProps) => {
  const [user, setUser] = useState<IUserData | null>(initialUser ?? null);
  const [event, setEvent] = useState<ICbEvent | null>(null);

  // Load event from hash?
  useEffect(() => {
    const hash = location.hash.substring(1);

    if (hash) {
      const event = parseStringToEvent(hash);

      if (event) {
        console.log(`Hash event:`, event);
        setEvent(event);
        location.hash = "";
      } else {
        console.log(`Invalid hash: '${hash}'`);
      }
    }
  }, []);

  // TODO set `defaultTab` to 'recent'
  return user
    ? <Main
      user={user}
      onLogout={() => setUser(null)}
      defaultTab={defaultTab}
      initialEvent={event ?? undefined}
    />
    : <Login
      onLoginSuccess={setUser}
    />;
};

export default App;
