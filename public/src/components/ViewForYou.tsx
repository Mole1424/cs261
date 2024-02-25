import {IUserData} from "../types/IUserData";
import {useEffect, useState} from "react";
import axios, {AxiosResponse} from "axios";
import {IUserCompany} from "../types/ICompany";

export interface IProps {
  user: IUserData;
}

export const ViewForYou = ({ user }: IProps) => {

  const [companies, setCompanies] = useState<IUserCompany[]>([]);

  useEffect(() => {
    requestSoftRecommendation()
      .then(response => {
        if (response) {
          setCompanies(response);
        } else {
          console.log("Failed to retrieve recommendations");
        }
      });
  }, []);


  return (
    <main className={'content-for-you'}>
      <span>Recommendations for {user.name}</span>
      {companies.map(company =>
          <span key={company.companyId}>Company #{company.companyId}</span>
        )}
    </main>
  );
};

export default ViewForYou;

/**
 * Attempt to fetch (soft) user recommendations.
 */
export async function requestSoftRecommendation() {
  try {
    const response = await axios.get('/user/for_you') as AxiosResponse<IUserCompany[], unknown>;
    return response.data;
  } catch {
    return null;
  }
}
