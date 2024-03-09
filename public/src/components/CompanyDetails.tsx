import {useEffect, useState} from "react";
import axios, {AxiosResponse} from "axios";
import {headerFormData} from "../constants";
import {ICompanyDetails, IFullCompanyDetails} from "../types/ICompany";
import {requestFollowCompany, requestUnfollowCompany} from "./CompanyCard";
import StockInformation from "./StockInformation";
import {getIconFromCategory} from "../util";

import DefaultCompanyIcon from "assets/company-default.svg";
import TrendUpIcon from "assets/trend-up.svg";
import TrendDownIcon from "assets/trend-down.svg";
import "styles/company-details.scss";
import ArticleCard from "./ArticleCard";
import IViewProps from "../types/IViewProps";

interface IProps {
  companyId: number;
}

export const CompanyDetails = ({ companyId, eventCallback }: (IViewProps & IProps)) => {
  const [company, setCompany] = useState<IFullCompanyDetails | null>(null);
  const [logoUrl, setLogoUrl] = useState<string | undefined>(undefined);
  const [isFollowing, setIsFollowing] = useState(false);
  const [stockIndex, setStockIndex] = useState(0);

  const [articleCount, setArticleCount] = useState(4);
  const [receivedArticleCount, setReceivedArticleCount] = useState(-1);

  /** Load company details. */
  const loadCompanyDetails = async (numberOfArticles?: number) => {
    const response = await requestCompanyDetails(companyId, numberOfArticles ?? articleCount);

    if (response && !response.error) {
      setCompany(response.data!);
      setLogoUrl(response.data!.logoUrl);
      setIsFollowing(response.data!.isFollowing);
      setReceivedArticleCount(response.data!.articles.length);
    }
  };

  useEffect(() => void loadCompanyDetails(), []);

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

  /** Click 'View More' link. */
  const clickViewMore = () => {
    setArticleCount(2 * articleCount);
    void loadCompanyDetails(2 * articleCount);
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
            {company.stockDelta == 0 ? '' : <img alt={'Stock trend icon'} src={company.stockDelta < 0 ? TrendDownIcon : TrendUpIcon} className={'icon style-' + (company.stockDelta < 0 ? 'red' : 'green')} />}
            <span>{Math.abs(company.stockDelta).toFixed(1)}%</span>
        </span>
        <span className={'company-sentiment'}>
          <img src={sentimentIcon} alt={company.sentimentCategory} className={'icon ' + sentimentIconClass} />
          <span>{company.sentiment}</span>
        </span>
        <span className={'company-ceo'}>{company.ceo}</span>
        <img className={'company-logo'} alt={'Company logo'} src={logoUrl} onError={() => setLogoUrl(DefaultCompanyIcon)} />
        <span className={'company-description'}>{company.description}</span>
          {company.stocks.length > 1 && <span className={'company-stock-exchange'}>
            <span>View stock data for exchange </span>
            <select onChange={e => setStockIndex(+e.target.value)}>
              {company.stocks.map((stock, idx) =>
                <option key={stock.exchange} value={idx}>{stock.exchange}</option>
              )}
            </select>
          </span>}

        {company.stocks && <StockInformation company={company} stock={company.stocks[stockIndex]} />}

        {company.articles.length && (
          <span className={'company-articles'}>
            <span>Here are some related news articles:</span>
            <div className={'content-cards'}>
              <div className={'cards'}>
                {company.articles.map(article =>
                  <ArticleCard key={article.id} article={article} eventCallback={eventCallback} />
                )}
              </div>
            </div>
            {(receivedArticleCount === articleCount) && (
              <span>
                <a onClick={clickViewMore} className={'link'}>View More</a>
              </span>
            )}
          </span>
        )}
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
export async function requestCompanyDetails(companyId: number, articleCount?: number) {
  try {
    const response = await axios.post('/company/details', {
      id: companyId,
      loadStock: true,
      articleCount
    }, headerFormData) as AxiosResponse<{
      data?: IFullCompanyDetails;
      error: boolean;
    }, unknown>;
    return response.data;
  } catch {
    return null;
  }
}
