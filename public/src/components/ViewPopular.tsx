import {IUserData} from "../types/IUserData";
import {useEffect, useState} from "react";
import {ICompanyDetails} from "../types/ICompany";
import CompanyCard, {requestUnfollowCompany} from "./CompanyCard";

import "styles/view-cards.scss";
import axios, {AxiosResponse} from "axios";
import {headerFormData} from "../constants";

export interface IProps {
  user: IUserData;
}

export const ViewPopular = ({ user }: IProps) => {
  const [companyCount, setCompanyCount] = useState(10);
  const [companies, setCompanies] = useState<ICompanyDetails[]>([]);
  const [receivedCompanyCount, setReceivedCompanyCount] = useState(-1);

  /** Populate `companies` state with `companyCount` companies. */
  const populateCompanies = async (count?: number) => {
    const response = await requestPopularCompanies(count ?? companyCount);

    if (response) {
      setCompanies(response);
      setReceivedCompanyCount(response.length);
    } else {
      console.log("Failed to retrieve popular companies");
      setReceivedCompanyCount(-1);
    }
  };

  // Load companies immediately
  useEffect(() => void populateCompanies(), []);

  /** Click 'View More' link. */
  const clickViewMore = () => {
    setCompanyCount(2 * companyCount);
    void populateCompanies(2 * companyCount);
  };

  return (
    <main className={'content-popular content-cards'}>
      <div className={'cards'}>
        {companies.map(company =>
          <CompanyCard key={company.id} company={company} />
        )}
        {(receivedCompanyCount === companyCount) && (
          <p style={{ display: 'flex', justifyContent: 'center' }}>
            <a onClick={clickViewMore} className={'link'}>View More</a>
          </p>
        )}
      </div>
    </main>
  );
};

export default ViewPopular;

/**
 * Attempt to fetch `count` most popular companies.
 */
export async function requestPopularCompanies(count: number) {
  try {
    const response = await axios.post('/company/popular', { count }, headerFormData) as AxiosResponse<ICompanyDetails[], unknown>;
    return response.data;
  } catch {
    return null;
  }
}
