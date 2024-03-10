import {IUserData} from "../types/IUserData";
import {useEffect, useState} from "react";
import {ICompanyDetails} from "../types/ICompany";
import CompanyCard from "./CompanyCard";

import "styles/view-cards.scss";
import axios, {AxiosResponse} from "axios";
import {headerFormData} from "../constants";
import IViewProps from "../types/IViewProps";
import {ILoadCompanyEvent} from "../types/AppEvent";
import {formatNumber} from "../util";

export const ViewFollowing = ({ eventCallback }: IViewProps) => {
  const [companies, setCompanies] = useState<ICompanyDetails[]>([]);

  // Load companies immediately
  useEffect(() => void requestFollowingCompanies()
    .then(response => response && setCompanies(response)), []);

  /** Click on a company card. */
  const clickCompanyCard = (companyId: number) =>
    eventCallback({
      type: 'load-company',
      companyId
    } as ILoadCompanyEvent);

  return (
    <main className={'content-following content-cards'}>
      <span className={'title-text'}>
        You are following {formatNumber(companies.length)} {companies.length === 1 ? "company" : "companies"}
      </span>

      {companies.length === 0
        ? <span>Click on the <em>Follow</em> button on a company card to follow a company.</span>
        : (
          <div className={'cards'}>
            {companies.map(company =>
              <CompanyCard key={company.id} company={company} onClick={clickCompanyCard} />
            )}
          </div>
        )}
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
