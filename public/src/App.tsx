import React from 'react';
import Login from "./components/Login";
import {IUserData} from "./interfaces/IUserData";
import {APP_NAME} from "./index";

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

  public render() {
    if (this.state.currentUser === null) {
      return <Login onLoginSuccess={this.setUser.bind(this)} />;
    } else {
      return <main className="app">
              <h1>Welcome to {APP_NAME}, {this.state.currentUser.name}!</h1>
              <br />
              <button onClick={this.clickLogout.bind(this)}>Log Out</button>
            </main>;
    }
  };
}
