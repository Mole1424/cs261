import {useEffect, useState} from "react";
import axios, {AxiosResponse} from "axios";
import {IUserCompanyDetails} from "../types/ICompany";
import IViewProps from "../types/IViewProps";
import CompanyCard from "./CompanyCard";
import {ILoadCompanyEvent} from "../types/AppEvent";

import "styles/view-cards.scss";
import {headerFormData} from "../constants";

export const ViewForYou = ({ eventCallback }: IViewProps) => {
  const [companyCount, setCompanyCount] = useState(5);
  const [receivedCompanyCount, setReceivedCompanyCount] = useState(-1);
  const [companies, setCompanies] = useState<IUserCompanyDetails[]>([]);

  /** Populate `companies` state with `companyCount` companies. */
  const populateCompanies = async (count?: number) => {
    const response = await requestSoftRecommendation(count ?? companyCount);

    if (response) {
      setCompanies(response);
      setReceivedCompanyCount(response.length);
    } else {
      console.log("Failed to retrieve recommendations");
      setReceivedCompanyCount(-1);
    }
  };

  useEffect(() => void populateCompanies(), []);

  /** Click on a company card. */
  const clickCompanyCard = (companyId: number) =>
    eventCallback({
      type: 'load-company',
      companyId
    } as ILoadCompanyEvent);

  /** Click 'View More' link. */
  const clickViewMore = () => {
    setCompanyCount(2 * companyCount);
    void populateCompanies(2 * companyCount);
  };

  return (
    <main className={'content-for-you content-cards'}>
      <span className={'title-text'}>
        Here are some companies you may be interested in.
      </span>
      <div className={'cards'}>
        {companies.map(data =>
          <CompanyCard
            key={data.companyId}
            company={data.company}
            onClick={clickCompanyCard}
          />
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

export default ViewForYou;

/**
 * Attempt to fetch (soft) user recommendations. Request to return `count` companies.
 */
export async function requestSoftRecommendation(count: number) {
  try {
    const response = await axios.post('/user/for-you', { count }, headerFormData) as AxiosResponse<IUserCompanyDetails[], unknown>;
    return response.data;
  } catch {
    return null;
  }
}
