import {IUserData} from "../types/IUserData";

export interface IProps {
  user: IUserData;
}

export const ViewSearch = ({ user }: IProps) => {
  return (
    <main className={'content-search'}>
      <span>Search</span>
    </main>
  );
};

export default ViewSearch;
