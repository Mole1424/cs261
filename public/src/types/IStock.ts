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

export type StockViewType = "day" | "week" | "month" | "year";

/** Given the stock view type, return numerical stock data. */
export function extractStockData(stock: IStock, type: StockViewType): number[] {
  switch (type) {
    case "day": return stock.stockDay;
    case "week": return stock.stockWeek;
    case "month": return stock.stockMonth;
    case "year": return stock.stockYear;
  }
}
