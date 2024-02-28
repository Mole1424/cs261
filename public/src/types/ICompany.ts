import ISector from "./ISector";
import SentimentCategory from "./SentimentCategory";
import IStock from "./IStock";

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

export interface ICompanyDetails extends ICompany {
  sectors: ISector[];
  stockDelta: number;
  isFollowing: boolean;
}

export interface ICompanyDetailsWithStock extends ICompany {
  sectors: ISector[];
  isFollowing: boolean;
  stock: IStock;
}

export interface IUserCompany {
  userId: number;
  companyId: number;
  distance: number;
}

