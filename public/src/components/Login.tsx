import {IUserData} from "../types/IUserData";
import {useState} from "react";
import axios, {AxiosError, AxiosResponse} from "axios";
import {headerFormData} from "../constants";
import ErrorCard from "./ErrorCard";

import "styles/login.scss"

interface IProps {
  onLoginSuccess: (user: IUserData) => void,
}

export const Login = ({ onLoginSuccess }: IProps) => {
  const [isSigningUp, setIsSigningUp] = useState(false); // Signing up, or logging in?
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [inputtedEmail, setInputtedEmail] = useState("");
  const [inputtedName, setInputtedName] = useState("");
  const [inputtedPassword, setInputtedPassword] = useState("");
  const [optEmail, setOptEmail] = useState(false);

  /** Click the 'Log In' button */
  const onClickLogin = async () => {
    const response = await requestLogin(inputtedEmail, inputtedPassword);
    setInputtedPassword("");

    if (response === null) {
      // Login failure.
      setErrorMessage("Incorrect email or password.");
    } else {
      // Login success.
      onLoginSuccess(response);
    }
  };

  /** Click the 'Create account' button */
  const onClickCreateAccount = async () => {
    const response = await requestCreateAccount(inputtedName, inputtedEmail, inputtedPassword, optEmail);

    if (response.error) {
      setErrorMessage(response.message!);
    } else {
      onLoginSuccess(response.user!);
    }
  };

  return (
    <main className="login">
      <div>
        <h1>{isSigningUp ? 'Sign Up' : 'Log In'}</h1>
        { errorMessage ? <ErrorCard messages={[errorMessage]} /> : "" }

        {isSigningUp && <input type="text" placeholder="Display name" value={inputtedName} onChange={e => {
          setInputtedName(e.target.value.trim());
        }} />}

        <input type="email" placeholder="Email" value={inputtedEmail} onChange={e => {
          setInputtedEmail(e.target.value.trim());
        }} />

        <input type="password" placeholder="Password" value={inputtedPassword} onChange={e => {
          setInputtedPassword(e.target.value.trim());
        }} />

        {isSigningUp && <span>
            <input type="checkbox" checked={optEmail} onChange={() => setOptEmail(!optEmail)} />
            Opt into daily email round-up
        </span>}

        {isSigningUp
          ? <button onClick={onClickCreateAccount}>Create Account</button>
          : <button onClick={onClickLogin}>Log In</button>
        }

        {!isSigningUp && <p>Don't have an account? <span className={'link'} onClick={() => {
          setErrorMessage(null);
          setIsSigningUp(true);
        }}>Sign up</span></p>}
      </div>
    </main>
  );
};

export default Login;

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

/**
 * Send request to create an account.
 */
export async function requestCreateAccount(name: string, email: string, password: string, optEmail: boolean) {
  try {
    const response = await axios.post('/user/create', { name, email, password, optEmail, loginAfter: true }, headerFormData) as AxiosResponse<{
      error: boolean;
      message?: string;
      user?: IUserData;
      loggedIn: boolean;
    }, unknown>;
    return response.data;
  } catch (e) {
    return {
      error: true,
      message: `Internal error (${(e as AxiosError).request.status})`,
      loggedIn: false
    };
  }
}
