import {IUserData} from "../types/IUserData";

export interface IProps {
  user: IUserData;
}

export const ViewFollowing = ({ user }: IProps) => {
  return (
    <main className={'content-following'}>
      <span>Following</span>
    </main>
  );
};

export default ViewFollowing;
