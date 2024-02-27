import {IUserData} from "../types/IUserData";
import {useEffect, useState} from "react";
import {ICompanyDetails} from "../types/ICompany";
import CompanyCard from "./CompanyCard";

import "styles/view-cards.scss";
import axios, {AxiosResponse} from "axios";
import {headerFormData} from "../constants";

export interface IProps {
  user: IUserData;
}

export const ViewFollowing = ({ user }: IProps) => {
  const [companies, setCompanies] = useState<ICompanyDetails[]>([]);

  // Load companies immediately
  useEffect(() => void requestFollowingCompanies()
    .then(response => response && setCompanies(response)), []);

  return (
    <main className={'content-following content-cards'}>
      <div className={'cards'}>
        {companies.map(company =>
          <CompanyCard key={company.id} company={company} />
        )}
      </div>
    </main>
  );
};

export default ViewFollowing;

/**
 * Attempt to fetch the companies we are following.
 * TODO add sorting
 */
export async function requestFollowingCompanies() {
  try {
    const response = await axios.post('/company/following', { }, headerFormData) as AxiosResponse<ICompanyDetails[], unknown>;
    return response.data;
  } catch {
    return null;
  }
}
