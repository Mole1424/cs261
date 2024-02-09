import {useState} from 'react';
import Login, {requestLogout} from "./components/Login";
import {IUserData} from "./types/IUserData";
import {APP_NAME} from "./index";
import TabGroup, {ITab} from "./components/TabGroup";
import {ViewComponentT} from "./types/ViewComponentT";

// @ts-ignore
import BellLogo from "assets/bell.svg";

// @ts-ignore
import RingingBellLogo from "assets/bell-ringing.svg";
import ViewFollowing from "./components/ViewFollowing";
import ViewForYou from "./components/ViewForYou";
import ViewRecent from "./components/ViewRecent";
import ViewPopular from "./components/ViewPopular";
import ViewSearch from "./components/ViewSearch";

export interface IAppProps {
  initialUser?: IUserData | null;
  defaultViewContent?: ViewComponentT; // Default content of view
  defaultTab?: string; // Label of the default tab
}

export interface IAppState {
  currentUser: IUserData | null;
  unreadNotificationCount: number;
  receivedNotification: boolean; // New unread notification (ringing bell icon?)
  viewContent: ViewComponentT | null;
}

export default function App(props: IAppProps) {
  const [state, setState] = useState<IAppState>({
    currentUser: props.initialUser ?? null,
    unreadNotificationCount: 0,
    receivedNotification: false,
    viewContent: props.defaultViewContent ?? null,
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
        label: 'Following',
        onClick: async () => {
          setState({ ...state, viewContent: ViewFollowing });
          return { select: true };
        }
      },
      {
        label: 'For You',
        onClick: async () => {
          setState({ ...state, viewContent: ViewForYou });
          return { select: true };
        }
      },
      {
        label: 'Recent',
        onClick: async () => {
          setState({ ...state, viewContent: ViewRecent });
          return { select: true };
        }
      },
      {
        label: 'Popular',
        onClick: async () => {
          setState({ ...state, viewContent: ViewPopular });
          return { select: true };
        }
      },
      {
        label: 'Search',
        onClick: async () => {
          setState({ ...state, viewContent: ViewSearch });
          return { select: true };
        }
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
          <TabGroup
            tabs={tabs}
            selected={props.defaultTab ? tabs.findIndex(tab => tab.label === props.defaultTab) : -1}/>
        </header>
        <main>
          {state.viewContent ? state.viewContent(state.currentUser) : ""}
        </main>
      </>
    );
  }
}
