import {useState} from 'react';
import Login, {requestLogout} from "./components/Login";
import {IUserData} from "./interfaces/IUserData";
import {APP_NAME} from "./index";
import TabGroup, {ITab} from "./components/TabGroup";

// @ts-ignore
import BellLogo from "assets/bell.svg";

// @ts-ignore
import RingingBellLogo from "assets/bell-ringing.svg";

export interface IAppProps {
  initialUser?: IUserData | null;
}

export interface IAppState {
  currentUser: IUserData | null;
  unreadNotificationCount: number;
  receivedNotification: boolean; // New unread notification (ringing bell icon?)
}

export default function App(props: IAppProps) {
  const [state, setState] = useState<IAppState>({
    currentUser: props.initialUser ?? null,
    unreadNotificationCount: 0,
    receivedNotification: false,
  });

  if (state.currentUser === null) {
    return <Login onLoginSuccess={user => void setState({ ...state, currentUser: user })} />;
  } else {
    /** Click the 'logout' button */
    const clickLogout = async () => {
      if (await requestLogout()) {
        setState({
          ...state,
          currentUser: null
        });
      }
    };

    /** Click the user's name */
    const clickUserName = () => {
      // TODO
      console.log("Click user's name");
      console.log(state.currentUser);
    };

    const clickBellIcon = async () => {
      // TODO
      console.log("Click bell icon");
    };

    const tabs: ITab[] = [
      {
        label: 'Following'
      },
      {
        label: 'For You'
      },
      {
        label: 'Recent'
      },
      {
        label: 'Popular'
      },
      {
        label: 'Search'
      },
      {
        label: 'Logout',
        onClick: async () => {
          await clickLogout();
          return { select: false };
        }
      }
    ];


    return (
      <>
        <header>
          <div>
            <div>
              <span>
                {APP_NAME}
              </span>
            </div>
            <div>
              <span onClick={clickUserName}>
                {state.currentUser.name}
              </span>
              <span onClick={clickBellIcon}>
                <img src={state.receivedNotification ? RingingBellLogo : BellLogo} alt="Bell Icon" title="View Notifications" />
                {state.unreadNotificationCount === 0 ? "" : <span>{state.unreadNotificationCount}</span>}
              </span>
            </div>
          </div>
          <TabGroup tabs={tabs}/>
        </header>
        <h1>Welcome to {APP_NAME}, {state.currentUser.name}!</h1>
        <p>This page is still under construction.</p>
      </>
    );
  }
}
