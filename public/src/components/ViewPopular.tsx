import {IUserData} from "../types/IUserData";

export interface IProps {
  user: IUserData;
}

export const ViewPopular = ({ user }: IProps) => {
  return (
    <main className={'content-popular'}>
      <span>Popular</span>
    </main>
  );
};

export default ViewPopular;
