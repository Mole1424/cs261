import {useState} from "react";
import {ICompanyDetails} from "../types/ICompany";
import axios from "axios";
import {headerFormData} from "../constants";

import DefaultCompanyIcon from "assets/company-default.svg";
import TrendUpIcon from "assets/trend-up.svg";
import TrendDownIcon from "assets/trend-down.svg";
import "styles/company-card.scss";

export const CompanyCard = ({ company }: { company: ICompanyDetails }) => {
  const [logoUrl, setLogoUrl] = useState(company.logoUrl);
  const [isFollowing, setIsFollowing] = useState(company.isFollowing);

  // const [sentimentIcon, sentimentIconClass] = getIconFromCategory(company.sentimentCategory);
  // const lastScraped = new Date(company.lastScraped);

  /** Click on the company card - - show more information. */
  const clickCard = () => {
    // TODO
    console.log("Click company card");
    console.log(company);
  };

  /** Click button to follow the given company. */
  const clickFollow = async (e: MouseEvent) => {
    e.stopPropagation();
    if (await requestFollowCompany(company.id)) {
      setIsFollowing(true);
    }
  };

  /** Click button to unfollow the given company. */
  const clickUnfollow = async (e: MouseEvent) => {
    e.stopPropagation();
   if (await requestUnfollowCompany(company.id)) {
     setIsFollowing(false);
   }
  };

  return <div className={'company-card'} data-company-id={company.id} onClick={clickCard}>
    <img className={'company-logo'} alt={'Company logo'} src={logoUrl} onError={() => setLogoUrl(DefaultCompanyIcon)} />
    <span className={'company-name'}>{company.name}</span>
    <span className={'company-stock'}>
      {company.stockDelta == 0 ? '' : <img alt={'Stock trend icon'} src={company.stockDelta < 0 ? TrendDownIcon : TrendUpIcon} className={'icon style-' + (company.stockDelta < 0 ? 'red' : 'green')} />}
      <span>{Math.abs(company.stockDelta).toFixed(1)}%</span>
    </span>
    {isFollowing
        ? <span className={'company-follow btn btn-danger'} onClick={e => clickUnfollow(e as unknown as MouseEvent)}>Unfollow</span>
        : <span className={'company-follow btn'} onClick={e => clickFollow(e as unknown as MouseEvent)}>Follow</span>}
    <span className={'company-sectors'}>
      <span>Sectors:</span>
      {company.sectors.map(sector =>
        <span className={'sector-tag'} key={sector.id}>
          {sector.name}
        </span>)}
    </span>
  </div>;
};

export default CompanyCard;

/**
 * Attempt to follow a company, return success.
 */
export async function requestFollowCompany(companyId: number) {
  try {
    await axios.post('/company/follow', { id: companyId }, headerFormData);
    return true;
  } catch {
    return false;
  }
}

/**
 * Attempt to unfollow a company, return success.
 */
export async function requestUnfollowCompany(companyId: number) {
  try {
    await axios.post('/company/unfollow', { id: companyId }, headerFormData);
    return true;
  } catch {
    return false;
  }
}
