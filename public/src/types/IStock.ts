export interface IStock {
  symbol: string;
  companyId: number;
  exchange: string;
  marketCap: number;
  stockPrice: number;
  stockChange: number;
  stockDay: number[];
  stockWeek: number[];
  stockMonth: number[];
  stockYear: number[];
}

export default IStock;
