import {IUserData} from "../types/IUserData";
import {useEffect, useState} from "react";
import ISector from "../types/ISector";
import axios, {AxiosError, AxiosResponse} from "axios";
import {headerFormData} from "../constants";
import ErrorCard from "./ErrorCard";

import "styles/user-profile.scss";
import PlusIcon from "assets/plus.svg";
import PencilIcon from "assets/pencil.svg";
import CheckIcon from "assets/check.svg";
import CrossIcon from "assets/cross.svg";

export interface IProps {
  user: IUserData;
}

export const UserProfile = ({ user }: IProps) => {
  const [userSectors, setUserSectors] = useState<ISector[] | undefined>();
  const [allSectors, setAllSectors] = useState<ISector[] | undefined>();
  const [isAddingSector, setIsAddingSector] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [inputtedPassword, setInputtedPassword] = useState("");
  const [inputtedNewPassword, setInputtedNewPassword] = useState("");
  const [inputtedNewPasswordRepeated, setInputtedNewPasswordRepeated] = useState("");
  const [userName, setUserName] = useState(user.name);
  const [editingName, setEditingName] = useState(false);
  

  /** Re-load userSectors and allSectors */
  const initialiseSectorStates = async () => {
    const userSectors = await requestUserSectors();
    const allSectors = await requestSectors();

    // Select all sectors which the user is not following
    const filteredSectors = allSectors.filter(s => userSectors.findIndex(us => s.id === us.id) === -1);

    setUserSectors(userSectors);
    setAllSectors(filteredSectors);
  };

  // Set sectors
  useEffect(() => void initialiseSectorStates(), []);

  /** Click on 'Change Password' */
  const clickChangePassword = async () => {
    const { error, message } = await requestChangePassword(inputtedPassword, inputtedNewPassword, inputtedNewPasswordRepeated);

    if (error) {
      setErrorMessage(message ?? null);
    } else {
      setErrorMessage(null);
      setInputtedPassword("");
      setInputtedNewPassword("");
      setInputtedNewPasswordRepeated("");
    }
  };

  /** Click on 'Delete Account' */
  const clickDeleteAccount = async () => {
    const deleted = await requestDeleteUser();

    if (deleted) {
      location.reload();
    } else {
      console.log("Error deleting account");
    }
  };

  /** Click on a sector tag */
  const clickSectorTag = async (sectorIndex: number, sector: ISector) => {
    if (await requestRemoveSector(sector)) {
      // Re-load sectors
      await initialiseSectorStates();
    } else {
      setErrorMessage(`Unable to remove sector ${sector.name}`);
      console.log(sector);
    }
  };

  /** Click to update display name */
  const clickUpdateDisplayName = async () => {
    const response = await requestChangeName(userName);

    if (response.error) {
      setErrorMessage(response.message!);
    } else {
      setUserName(response.user!.name);
      user.name = response.user!.name;
      setEditingName(false);
    }
  };

  /** Add sector: select sector */
  const onSelectAddSector = async (sectorId: number) => {
    const response = await requestAddSector(sectorId);

    if (response.error) {
      setErrorMessage(response.message ?? null);
    } else {
      // Re-populate sector list
      setIsAddingSector(false);
      await initialiseSectorStates();
    }
  };


  return (
    <main className={'content-user-profile'}>
      <span className={'title'}>Hello, {userName}</span>
      {errorMessage && <ErrorCard messages={[errorMessage]} />}
      <div>
        <span>Display name:</span>
        <span>{editingName
          ? <input type={'text'} value={userName} onChange={e => setUserName(e.target.value.trim())} />
          : userName
        }</span>
        <span>
          {editingName
            ? <>
                <img src={CheckIcon} alt={'Update name'} onClick={clickUpdateDisplayName} className={'icon style-green'} />
                <img src={CrossIcon} alt={'Revert change'} onClick={() => {
                  setUserName(user.name);
                  setEditingName(false);
                }} className={'icon style-red'} />
              </>
            : <img src={PencilIcon} alt={'Change name'} onClick={() => setEditingName(true)} className={'icon'} />
          }
        </span>

        <span>Email:</span>
        <span>{user.email}</span>
        <span/>

        <span>Interested Sectors:</span>
        <span className={'section-sectors'}>
          {userSectors?.map((sector, index) =>
            <span className={'sector-tag btn btn-danger'} key={sector.id} onClick={() => clickSectorTag(index, sector)}>
              {sector.name}
            </span>
          )}
          {isAddingSector
            ? <>
              <select defaultValue={'_default'} onChange={e => onSelectAddSector(+e.target.value)}>
                <option value="_default" disabled>Select One</option>
                {allSectors && allSectors.map(({ id, name }) => <option value={id} key={id}>{name}</option>)}
              </select>
              <img src={CrossIcon} alt={'Cancel'} onClick={() => setIsAddingSector(false)} className={'icon style-red'} />
            </>
            : <img src={PlusIcon} alt={'Add new sector'} onClick={() => setIsAddingSector(true)} className={'icon'} />
          }
        </span>
        <span/>

        <span>Password:</span>
        <span className={'section-password'}>
          <input
            type={'password'}
            placeholder={'Password'}
            value={inputtedPassword}
            onChange={e => setInputtedPassword(e.target.value.trim())}
          />
          <input
            type={'password'}
            placeholder={'New password'}
            value={inputtedNewPassword}
            onChange={e => setInputtedNewPassword(e.target.value.trim())}
          />
          <input
            type={'password'}
            placeholder={'Repeat new password'}
            value={inputtedNewPasswordRepeated}
            onChange={e => setInputtedNewPasswordRepeated(e.target.value.trim())}
          />
        </span>
        <span>
          <button onClick={clickChangePassword}>Change password</button>
        </span>

        <span/>
        <button className={'btn-danger'} onClick={clickDeleteAccount}>Delete Account</button>
        <span/>
      </div>
    </main>
  );
};

export default UserProfile;

/**
 * Send request to delete the current user. Return success.
 */
export async function requestDeleteUser(): Promise<boolean> {
  try {
    const response = await axios.post('/user/delete');
    return true;
  } catch {
    return false;
  }
}

/**
 * Send request to change user's password. Return OK or error message.
 */
export async function requestChangePassword(password: string, newPassword: string, repeatNewPassword: string) {
  try {
    return (await axios.post('/user/change-password', {
      password,
      newPassword,
      repeatNewPassword
    }, headerFormData) as AxiosResponse<{ error: boolean, message?: string }, unknown>).data;
  } catch (e) {
    return { error: true, message: "Internal error (" + (e as AxiosError).request.status + ")" };
  }
}

/**
 * Send request to change user's name.
 */
export async function requestChangeName(name: string) {
  try {
    return (await axios.post('/user/change-name', { name }, headerFormData) as AxiosResponse<{ error: boolean, message?: string, user?: IUserData }, unknown>).data;
  } catch (e) {
    return { error: true, message: "Internal error (" + (e as AxiosError).request.status + ")" };
  }
}

/**
 * Get list of all available sectors.
 */
export async function requestSectors() {
  try {
    return (await axios.get('/data/sectors') as AxiosResponse<ISector[], unknown>).data;
  } catch {
    return [];
  }
}

/**
 * Send request to get the current user's sectors.
 */
export async function requestUserSectors() {
  try {
    return (await axios.get('/user/sectors/get') as AxiosResponse<ISector[], unknown>).data;
  } catch {
    return [];
  }
}

/**
 * Send request to add the given sector ID to the user's profile
 */
export async function requestAddSector(sectorId: number) {
  try {
    return (await axios.post('/user/sectors/add', { id: sectorId }, headerFormData) as AxiosResponse<{
      error: boolean;
      message?: string;
      sector?: ISector;
    }, unknown>).data;
  } catch (e) {
    return { error: true, message: `Internal error (${(e as AxiosError).request.status})` };
  }
}

/**
 * Send request to delete the given sector from the user's profile.
 */
export async function requestRemoveSector(sector: ISector) {
  try {
    await axios.post('/user/sectors/remove', { id: sector.id }, headerFormData);
    return true;
  } catch {
    return false;
  }
}
