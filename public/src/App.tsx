import {useState} from 'react';
import Login, {requestLogout} from "./components/Login";
import {IUserData} from "./interfaces/IUserData";
import {APP_NAME} from "./index";
import TabGroup, {ITab} from "./components/TabGroup";

export interface IAppProps {
  initialUser?: IUserData | null;
}

export interface IAppState {
  currentUser: IUserData | null;
}

export default function App(props: IAppProps) {
  const [state, setState] = useState<IAppState>({
    currentUser: props.initialUser ?? null
  });

  /** Click the 'logout' button */
  const clickLogout = async () => {
    if (await requestLogout()) {
      setState({
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

  if (state.currentUser === null) {
    return <Login onLoginSuccess={user => void setState({ currentUser: user })} />;
  } else {
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
            <span>
              {APP_NAME}
            </span>
            <span onClick={clickUserName}>
              {state.currentUser.name}
            </span>
            <span>
              TODO: Bell
            </span>
          </div>
          <TabGroup tabs={tabs} />
        </header>
        <h1>Welcome to {APP_NAME}, {state.currentUser.name}!</h1>
        <p>This page is still under construction.</p>
      </>
    );
  }
}
