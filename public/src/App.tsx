import React from 'react';
import Login from "./components/Login";
import {IUserData} from "./interfaces/IUserData";
import {APP_NAME} from "./index";
import TabGroup, {ITab} from "./components/TabGroup";

export interface IAppProps {
  initialUser?: IUserData | null;
}

export interface IAppData {
  currentUser: IUserData | null;
}

export default class App extends React.Component<IAppProps, IAppData> {
  constructor(props: IAppProps) {
    super(props);
    this.state = {
      currentUser: props.initialUser ?? null
    };
  }

  public setUser(user: IUserData | null) {
    this.setState({
      currentUser: user
    });
  }

  /** Click the 'logout' button */
  private async clickLogout() {
    if (await Login.requestLogout()) {
     this.setUser(null);
    }
  }

  /** Click the user's name */
  private clickUserName() {
    // TODO
    console.log("Click user's name");
    console.log(this.state.currentUser);
  }

  public render() {
    if (this.state.currentUser === null) {
      return <Login onLoginSuccess={this.setUser.bind(this)} />;
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
            await this.clickLogout();
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
              <span onClick={this.clickUserName.bind(this)}>
                {this.state.currentUser.name}
              </span>
              <span>
                TODO: Bell
              </span>
            </div>
            <TabGroup tabs={tabs} />
          </header>
          <h1>Welcome to {APP_NAME}, {this.state.currentUser.name}!</h1>
          <p>This page is still under construction.</p>
        </>
      );
    }
  };
}
