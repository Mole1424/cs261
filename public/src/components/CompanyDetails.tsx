import {useEffect, useState} from "react";
import axios, {AxiosResponse} from "axios";
import {headerFormData} from "../constants";
import {ICompanyDetailsWithStock} from "../types/ICompany";
import {requestFollowCompany, requestUnfollowCompany} from "./CompanyCard";
import StockInformation from "./StockInformation";
import {getIconFromCategory} from "../util";

import DefaultCompanyIcon from "assets/company-default.svg";
import TrendUpIcon from "assets/trend-up.svg";
import TrendDownIcon from "assets/trend-down.svg";
import "styles/company-details.scss";

interface IProps {
  companyId: number;
}

export const CompanyDetails = ({ companyId }: IProps) => {
  const [company, setCompany] = useState<ICompanyDetailsWithStock | null>(null);
  const [logoUrl, setLogoUrl] = useState<string | undefined>(undefined);
  const [isFollowing, setIsFollowing] = useState(false);

  useEffect(() => void requestCompanyDetails(companyId)
    .then(response => {
      if (response && !response.error) {
        setCompany(response.data!);
        setLogoUrl(response.data!.logoUrl);
        setIsFollowing(response.data!.isFollowing);
      }
    }), []);

  /** Click button to follow the given company. */
  const clickFollow = async (e: MouseEvent) => {
    e.stopPropagation();
    if (company && await requestFollowCompany(company.id)) {
      setIsFollowing(true);
    }
  };

  /** Click button to unfollow the given company. */
  const clickUnfollow = async (e: MouseEvent) => {
    e.stopPropagation();
   if (company && await requestUnfollowCompany(company.id)) {
     setIsFollowing(false);
   }
  };

  if (company) {
    const [sentimentIcon, sentimentIconClass] = getIconFromCategory(company.sentimentCategory);

    return <main className={'company-details'} data-company-id={companyId}>
        <span className={'company-name'}>{company.name}</span>
        <span className={'company-url'}><a href={company.url} target="_blank" className="link">{company.url}</a></span>
        {isFollowing
          ? <span className={'company-follow btn btn-danger'} onClick={e => clickUnfollow(e as unknown as MouseEvent)}>Unfollow</span>
          : <span className={'company-follow btn'} onClick={e => clickFollow(e as unknown as MouseEvent)}>Follow</span>}
        <span className={'company-sectors'}>
        {company.sectors.length === 0
          ? <span>No sectors</span>
          : <>
            <span>Sectors:</span>
            {company.sectors.map(sector =>
              <span className={'sector-tag'} key={sector.id}>
                {sector.name}
              </span>)}
          </>
        }
        <span className={'company-stock-change'}>
          {company.stock
            ? <>
              {company.stock.stockChange == 0 ? '' : <img alt={'Stock trend icon'} src={company.stock.stockChange < 0 ? TrendDownIcon : TrendUpIcon} className={'icon style-' + (company.stock.stockChange < 0 ? 'red' : 'green')} />}
              <span>{Math.abs(company.stock.stockChange).toFixed(1)}%</span>
            </>
            : 'Stock Data Unavailable'}
        </span>
        <span className={'company-sentiment'}>
          <img src={sentimentIcon} alt={company.sentimentCategory} className={'icon ' + sentimentIconClass} />
          <span>{company.sentiment}</span>
        </span>
        <span className={'company-ceo'}>{company.ceo}</span>
        <img className={'company-logo'} alt={'Company logo'} src={logoUrl} onError={() => setLogoUrl(DefaultCompanyIcon)} />
        <span className={'company-description'}>{company.description}</span>

        {company.stock && <StockInformation company={company} stock={company.stock} />}
      </span>
    </main>;
  } else {
    return <main className={'company-details'} data-company-id={companyId}>
      <p>Loading...</p>
    </main>;
  }
};

export default CompanyDetails;

/**
 * Attempt to fetch details on the given company.
 */
export async function requestCompanyDetails(companyId: number) {
  try {
    const response = await axios.post('/company/details', {
      id: companyId,
      loadStock: true
    }, headerFormData) as AxiosResponse<{
      data?: ICompanyDetailsWithStock;
      error: boolean;
    }, unknown>;
    return response.data;
  } catch {
    return null;
  }
}
