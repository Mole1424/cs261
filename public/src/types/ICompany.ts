import ISector from "./ISector";
import SentimentCategory from "./SentimentCategory";

export interface ICompany {
  id: number;
  name: string;
  url: string;
  logoUrl: string;
  description: string;
  location: string;
  marketCap: number; // USD
  ceo: string;
  sentiment: number;  // |x| <= 1
  sentimentCategory: SentimentCategory;
  lastScraped: string; // Date
}

export default ICompany;

export interface ICompanyDetails extends ICompany {
    sectors: ISector[];
    stockDelta: number;
    isFollowing: boolean;
}
