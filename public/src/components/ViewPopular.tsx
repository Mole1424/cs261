import {useEffect, useState} from "react";
import {ICompanyDetails} from "../types/ICompany";
import CompanyCard from "./CompanyCard";
import axios, {AxiosResponse} from "axios";
import {headerFormData} from "../constants";
import {ILoadCompanyEvent} from "../types/AppEvent";
import IViewProps from "../types/IViewProps";

import "styles/view-cards.scss";

export const ViewPopular = ({ eventCallback }: IViewProps) => {
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

  /** Click on a company card. */
  const clickCompanyCard = (companyId: number) =>
    eventCallback({
      type: 'load-company',
      companyId
    } as ILoadCompanyEvent);

  return (
    <main className={'content-popular content-cards'}>
      <span className={'title-text'}>
        Here are some companies that are popular at the moment.
      </span>
      <div className={'cards'}>
        {companies.map(company =>
          <CompanyCard key={company.id} company={company} onClick={clickCompanyCard} />
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
