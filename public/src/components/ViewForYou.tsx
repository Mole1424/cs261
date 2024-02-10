import {IUserData} from "../types/IUserData";

export interface IProps {
  user: IUserData;
}

export const ViewForYou = ({ user }: IProps) => {
  return (
    <main className={'content-for-you'}>
      <span>For You</span>
    </main>
  );
};

export default ViewForYou;
