import {IUserData} from "../types/IUserData";
import {useState} from "react";
import axios, {AxiosResponse} from "axios";
import {headerFormData} from "../constants";
import ErrorCard from "./ErrorCard";

import "styles/login.scss"

interface ILoginProps {
  onLoginSuccess: (user: IUserData) => void,
}

interface ILoginState {
  errorMessage: string | null;
}

export default function Login(props: ILoginProps) {
  let inputtedEmail = "";
  let inputtedPassword = "";

  const [state, setState] = useState<ILoginState>({
    errorMessage: ""
  });

  /** Click the 'Log In' button */
  const onClickLogin = async () => {
    const response = await requestLogin(inputtedEmail, inputtedPassword);

    if (response === null) {
      // Login failure.
      setState({ errorMessage: "Incorrect email or password." });
    } else {
      // Login success.
      props.onLoginSuccess(response);
    }
  }

  return (
    <main className="login">
      <div>
        { state.errorMessage ? <ErrorCard messages={[state.errorMessage]} /> : "" }

        <input type="email" placeholder="Email" onChange={e => {
          inputtedEmail = e.target.value.trim();
        }} />

        <input type="password" placeholder="Password" onChange={e => {
          inputtedPassword = e.target.value.trim();
        }} />

        <button onClick={onClickLogin}>Log In</button>
      </div>
    </main>
  );
}

/**
 * Return the current logged-in user for this session, or null.
 */
export async function getCurrentUserData(): Promise<IUserData | null> {
  try {
    const response = await axios.get('/user') as AxiosResponse<IUserData, unknown>;
    return response.data;
  } catch (e: unknown) {
    // Error: 401 (no user)
    return null;
  }
}

/**
 * Send request to log in. Return either new logged-in user, or return failure.
 */
export async function requestLogin(email: string, password: string): Promise<IUserData | null> {
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
export async function requestLogout(): Promise<boolean> {
  try {
    await axios.get('/auth/logout');
    return true;
  } catch {
    return false;
  }
}
