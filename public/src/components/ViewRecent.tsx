import {IUserData} from "../types/IUserData";

export interface IProps {
  user: IUserData;
}

export const ViewRecent = ({ user }: IProps) => {
  return (
    <main className={'content-recent'}>
      <span>Recent</span>
    </main>
  );
};

export default ViewRecent;
