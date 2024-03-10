import IViewProps from "../types/IViewProps";
import {useEffect, useState} from "react";
import axios, {AxiosResponse} from "axios";
import {headerFormData} from "../constants";
import {ICompanyDetails} from "../types/ICompany";
import CompanyCard from "./CompanyCard";
import {ILoadCompanyEvent} from "../types/AppEvent";
import {requestSectors} from "./UserProfile";
import {arrayRemove} from "../util";
import ISector from "../types/ISector";
import Loading from "assets/loading.svg";

import "styles/view-search.scss";
import PlusIcon from "assets/plus.svg";
import CrossIcon from "assets/cross.svg";

export const ViewSearch = ({ eventCallback }: IViewProps) => {
  const [companies, setCompanies] = useState<ICompanyDetails[]>([]);
  const[sectors, setSectors] = useState<ISector[]>([]);
  const [loading, setLoading] = useState(false); 

  /** Search for companies. */
const onSearch = (fields: ISearchOptions) => {
  // Check if any search criteria have been entered
  const hasSearchCriteria =
    fields.ceo ||
    fields.name ||
    (fields.sectors && fields.sectors.length > 0) ||
    (fields.sentimentRange && (fields.sentimentRange[0] !== -1 || fields.sentimentRange[1] !== 1)) ||
    (fields.marketCap && (fields.marketCap[0] !== 0 || fields.marketCap[1] !== 0)) ||
    (fields.stockPriceRange && (fields.stockPriceRange[0] !== 0 || fields.stockPriceRange[1] !== 0));

  if (hasSearchCriteria) {
    setLoading(true);
    console.log(fields); // ! DEBUG
    requestSearchCompanies(fields)
      .then((response) => {
        if (response) {
          setCompanies(response);
        } else {
          console.log("Failed to search for companies.");
        }
      })
      .finally(() => setLoading(false));
  }
};

  /** Click on a company card. */
  const clickCompanyCard = (companyId: number) =>
    eventCallback({
      type: 'load-company',
      companyId
    } as ILoadCompanyEvent);

  // Trigger initial search
  useEffect(() => {
    // onSearch({});

    requestSectors()
      .then(response => response && setSectors(response));
  }, []);

  return (
    <div className={'content-search content-cards'}>
      <SearchOptions
        onChange={onSearch}
        sectors={sectors}
        initialSentimentScore={1}
        initialMarketCap={1_000_000_000_000}
        initialStockPrice={1_000}
      />

<div className={'cards'}>
  {loading ? (
    <img
      src={Loading}
      alt={"Loading"}
      style={{ width: '4%', height: '4%', display: 'block', margin: 'auto' }}
      className={`rotate-animation loading-icon`}
    />
  ) : (
    companies.map((company) => (
      <CompanyCard
        key={company.id}
        company={company}
        onClick={clickCompanyCard}
      />
    ))
  )}
</div>
</div>
  );
};

export default ViewSearch;

interface ISearchOptionsProps {
  onChange: (opts: ISearchOptions) => void;
  sectors: ISector[];
  initialStockPrice: number;
  initialMarketCap: number;
  initialSentimentScore: number;
}

interface ISearchOptions {
  ceo?: string;
  name?: string; // Company name.
  sectors?: number[]; // List of sector IDs.
  sentimentRange?: [number, number]; // [lower, upper) of sentiment score.
  marketCap?: [number, number]; // [lower, upper) of market cap.
  stockPriceRange?: [number, number]; // [lower, upper) of stock price.
}

/** Search component. */
const SearchOptions = (props: ISearchOptionsProps) => {
  const [fieldCeo, setFieldCeo] = useState('');
  const [fieldCompanyName, setFieldCompanyName] = useState('');
  const [fieldSentimentLower, setFieldSentimentLower] = useState(-props.initialSentimentScore);
  const [fieldSentimentUpper, setFieldSentimentUpper] = useState(props.initialSentimentScore);
  const [fieldMarketCapLower, setFieldMarketCapLower] = useState(0);
  const [fieldMarketCapUpper, setFieldMarketCapUpper] = useState(props.initialMarketCap);
  const [fieldStockPriceLower, setFieldStockPriceLower] = useState(0);
  const [fieldStockPriceUpper, setFieldStockPriceUpper] = useState(props.initialStockPrice);
  const [fieldSectors, setFieldSectors] = useState<number[]>([]);
  const [isAddingSector, setIsAddingSector] = useState(false);

  /** Request companies with entered parameters. */
  const callOnChange = () => {
    const payload = {} as ISearchOptions;

    if (fieldCeo.length > 0) payload.ceo = fieldCeo;
    if (fieldCompanyName.length > 0) payload.name = fieldCompanyName;
    if (fieldSectors.length > 0) payload.sectors = fieldSectors;

    payload.sentimentRange = [fieldSentimentLower, fieldSentimentUpper];
    payload.marketCap = [fieldMarketCapLower, fieldMarketCapUpper];
    payload.stockPriceRange = [fieldStockPriceLower, fieldStockPriceUpper];

    props.onChange(payload);
  };

  useEffect(callOnChange, []);

  /** Add new sector. */
  const addSector = (sectorId: number) => {
    if (fieldSectors.indexOf(sectorId) === -1)
      setFieldSectors(s => s.concat([sectorId]));
  };

  return (
    <div className={'search-options'}>
      <span className={'search-ceo'}>
        <span>Company CEO:</span>
        <input type="text" placeholder={'CEO'} onChange={e => setFieldCeo(e.target.value.trim())} />
      </span>

      <span className={'search-name'}>
        <span>Company name:</span>
        <input type="text" placeholder={'Company Name'} onChange={e => setFieldCompanyName(e.target.value.trim())} />
      </span>

      <span className={'search-sectors'}>
        <span>Sectors:</span>
        {fieldSectors.map((sectorId, index) =>
          <span key={sectorId}>
            <select defaultValue={sectorId} onChange={e => setFieldSectors(ss => {
              const copy = [...ss];
              copy[index] = sectorId;
              return copy;
            })}>
              {props.sectors.map(sector =>
                <option key={sector.id} value={sector.id}>{sector.name}</option>
              )}
            </select>
            <img src={CrossIcon} alt={'Remove'} onClick={() => {
              setFieldSectors(ss => arrayRemove([...ss], sectorId));
            }} className={'icon style-red'} />
          </span>
        )}
        {isAddingSector
          ? <>
            <select defaultValue={'_default'} onChange={e => {
              addSector(+e.target.value);
              setIsAddingSector(false);
            }}>
              <option value="_default" disabled>Select One</option>
              {props.sectors.map(({ id, name }) => fieldSectors.indexOf(id) === -1 && <option value={id} key={id}>{name}</option>)}
            </select>
            <img src={CrossIcon} alt={'Cancel'} onClick={() => setIsAddingSector(false)} className={'icon style-red'} />
          </>
          : <img src={PlusIcon} alt={'Add new sector'} onClick={() => setIsAddingSector(true)} className={'icon'} />
        }
      </span>

      <span className={'search-sentiment'}>
        <span>Sentiment score:</span>
        <span className={'range-slider'}>
          <input value={fieldSentimentLower} min={-1} max={1} step={0.1} type="range" onChange={e => setFieldSentimentLower(+e.target.value)} />
          <input value={fieldSentimentUpper} min={-1} max={1} step={0.1} type="range" onChange={e => setFieldSentimentUpper(+e.target.value)} />
        </span>
        <span>{fieldSentimentLower} to {fieldSentimentUpper}</span>
      </span>

      <span className={'search-market-cap'}>
        <span>Market capitalisation:</span>
        <span>
          $ <input type="number" value={fieldMarketCapLower} min={0} onChange={e => setFieldMarketCapLower(+e.target.value)} />
        </span>
        <span>to</span>
        <span>
          $ <input type="number" value={fieldMarketCapUpper} onChange={e => setFieldMarketCapUpper(+e.target.value)} />
        </span>
      </span>

      <span className={'search-stock-price'}>
        <span>Stock price:</span>
        <span>
          $ <input type="number" value={fieldStockPriceLower} min={0} onChange={e => setFieldStockPriceLower(+e.target.value)} />
        </span>
        <span>to</span>
        <span>$ <input type="number" value={fieldStockPriceUpper} onChange={e => setFieldStockPriceUpper(+e.target.value)} /></span>
      </span>

      <span className={'search-button-container'}>
        <button onClick={callOnChange}>Search</button>
      </span>
    </div>
  );
};

/**
 * Search for companies using the given parameters.
 */
export async function requestSearchCompanies(params: ISearchOptions) {
  try {
    const response = await axios.post('/company/search', params, headerFormData) as AxiosResponse<ICompanyDetails[], unknown>;
    return response.data;
  } catch {
    return null;
  }
}