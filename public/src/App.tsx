import React, {useState} from 'react';
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
import {ICbEvent, ILoadCompanyEvent} from "./types/AppEvent";
import CompanyDetails from "./components/CompanyDetails";
import Interface from "./components/Interface";

interface IProps {
  initialUser?: IUserData | null,
  defaultTab?: string; // Label of the default tab
}

export const App = ({ initialUser, defaultTab }: IProps) => {
  const [user, setUser] = useState<IUserData | null>(initialUser ?? null);

  // TODO set `defaultTab` to 'recent'
  return user
    ? <Interface user={user} onLogout={() => setUser(null)} defaultTab={defaultTab} />
    : <Login onLoginSuccess={setUser} />;
};

export default App;
