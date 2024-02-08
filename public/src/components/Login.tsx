import {IUserData} from "../interfaces/IUserData";
import React from "react";
import axios, {AxiosResponse} from "axios";
import {headerFormData} from "../constants";
import "styles/login.scss"
import ErrorCard from "./ErrorCard";

interface ILoginProps {
  onLoginSuccess: (user: IUserData) => void,
}

interface ILoginState {
  errorMessage: string | null;
}

export default class Login extends React.Component<ILoginProps, ILoginState> {
  private inputtedEmail = "";
  private inputtedPassword = "";

  constructor(props: ILoginProps) {
    super(props);
    this.state = {
      errorMessage: ""
    };
  }

  private async onClickLogin() {
    const response = await Login.requestLogin(this.inputtedEmail, this.inputtedPassword);

    if (response === null) {
      // Login failure.
      this.setState({ errorMessage: "Incorrect email or password." });
    } else {
      // Login success.
      this.props.onLoginSuccess(response);
    }
  }

  public render() {
    return (
      <main className="login">
        <div>
          { this.state.errorMessage ? <ErrorCard messages={["Incorrect email or password."]} /> : "" }

          <input type="email" placeholder="Email" onChange={e => {
            this.inputtedEmail = e.target.value.trim();
          }} />

          <input type="password" placeholder="Password" onChange={e => {
            this.inputtedPassword = e.target.value.trim();
          }} />

          <button onClick={this.onClickLogin.bind(this)}>Log In</button>
        </div>
      </main>
    );
  }

  /**
   * Return the current logged-in user for this session, or null.
   */
  public static async getCurrentUserData(): Promise<IUserData | null> {
    try {
      const response = await axios.get('/auth/get') as AxiosResponse<IUserData, unknown>;
      return response.data;
    } catch (e: unknown) {
      // Error: 401 (no user)
      return null;
    }
  }

  /**
   * Send request to log in. Return either new logged-in user, or return failure.
   */
  public static async requestLogin(email: string, password: string): Promise<IUserData | null> {
    try {
      const response = await axios.post('/auth/login', { email, password }, headerFormData) as AxiosResponse<IUserData, unknown>;
      return response.data;
    } catch {
      return null;
    }
  }

  /**
   * Send request to log the user out, return success.
   */
  public static async requestLogout(): Promise<boolean> {
    try {
      await axios.get('/auth/logout');
      return true;
    } catch {
      return false;
    }
  }
}
