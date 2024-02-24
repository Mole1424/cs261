import ICompany from "../types/ICompany";
import {IUserData} from "../types/IUserData";
import {useEffect, useState} from "react";
import axios, {AxiosResponse} from "axios";

export interface IProps {
  user: IUserData;
}

export const ViewForYou = ({ user }: IProps) => {

  const [Companies, setCompanies] = useState<ICompany[]>([]);

  useEffect(() => {
    requestsoftRecommendation()
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
      {Companies.map(company => 
          company.company_id
        )}
    </main>
  );
};

export default ViewForYou;

/**
 * Attempt to fetch recent news articles.
 */
export async function requestsoftRecommendation() {
  try {
    const response = await axios.get('/user/for_you') as AxiosResponse<ICompany[], unknown>;
    return response.data;
  } catch {
    return null;
  }
}
