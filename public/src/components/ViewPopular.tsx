import {IUserData} from "../types/IUserData";
import {useEffect, useState} from "react";
import {ICompanyDetails} from "../types/ICompany";
import CompanyCard from "./CompanyCard";

import "styles/view-cards.scss";
import axios, {AxiosResponse} from "axios";

export interface IProps {
  user: IUserData;
}

export const ViewPopular = ({ user }: IProps) => {
  const [companies, setCompanies] = useState<ICompanyDetails[]>([]);

  useEffect(() => {
    requestPopularCompanies()
      .then(response => {
        if (response) {
          setCompanies(response);
        } else {
          console.log("Failed to retrieve popular companies");
        }
      });
  }, []);

  return (
    <main className={'content-popular content-cards'}>
      <div className={'cards'}>
        {companies.map(company =>
          <CompanyCard key={company.id} company={company} />
        )}
      </div>
    </main>
  );
};

export default ViewPopular;

/**
 * Attempt to fetch popular companies.
 */
export async function requestPopularCompanies() {
  try {
    const response = await axios.get('/company/popular') as AxiosResponse<ICompanyDetails[], unknown>;
    return response.data;
  } catch {
    return null;
  }
}
