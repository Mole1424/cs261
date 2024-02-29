import IStock, {extractStockData, StockViewType} from "../types/IStock";
import {useState} from "react";
import {ICompany} from "../types/ICompany";
import {calculateMean, capitalise, createDateArray, formatDate, formatDateTime, formatNumber} from "../util";
import ChartAnnotation from "chartjs-plugin-annotation";
import Chart, {ChartOptions} from "chart.js/auto";
import { Line } from "react-chartjs-2";

import "styles/stock-information.scss";

// Register annotations plugin
Chart.register(ChartAnnotation);

interface IProps {
  company: ICompany;
  stock: IStock;
}

export const StockInformation = ({ stock, company }: IProps) => {
  const [stockViewType, setStockViewType] = useState<StockViewType>("day");

  return <div className={'stock-information'} data-company-id={stock.companyId}>
    <span className={'stock-title'}>Stock data for {company.name}</span>
    <span className={'stock-about'}>Stock {stock.symbol} is traded at {stock.exchange}</span>
    <span className={'stock-current'}>Currently, {stock.symbol} stocks are worth ${formatNumber(stock.stockPrice)} ({formatNumber(stock.stockChange)}%) with a market cap of ${formatNumber(stock.marketCap)}</span>
    <span className={'stock-select-range'}>
      <span>View history:</span>
      {(["day", "week", "month", "year"] as StockViewType[]).map(type =>
        <span key={type}>
          {capitalise(type)}
          <input
            type="radio"
            name="stock-view-range"
            checked={type === stockViewType}
            onChange={() => setStockViewType(type)}
          />
        </span>)}
    </span>

    <span className={'stock-graph-container'}>
      {generateLineGraph(stock, stockViewType)}
    </span>
  </div>
};

export default StockInformation;

/** Given a stock type, return [start, end] dates. */
function stockTypeToDates(type: StockViewType): [Date, Date] {
 switch (type) {
   case "day":
     return [
       new Date(Date.now() - 1000 * 60 * 60 * 24),
       new Date()
     ];
   case "week":
     return [
       new Date(Date.now() - 1000 * 60 * 60 * 24 * 7),
       new Date()
     ];
   case "month":
     return [
       (function () {
         const date = new Date();
         date.setMonth(date.getMonth() - 1);
         return date;
       })(),
       new Date()
     ];
   case "year":
     return [
       (function () {
         const date = new Date();
         date.setFullYear(date.getFullYear() - 1);
         return date;
       })(),
       new Date()
     ];
 }
}

/** Generate line chart. */
function generateLineGraph(stock: IStock, type: StockViewType) {
  const stockData = extractStockData(stock, type);
  const minimum = Math.min.apply(null, stockData);
  const maximum = Math.max.apply(null, stockData);
  const mean = calculateMean(stockData);

  const data = {
      labels: createDateArray(...stockTypeToDates(type), stockData.length).map(type === "day" ? formatDateTime : formatDate),
      datasets: [
        {
          label: stock.symbol,
          data: stockData
        }
      ]
    };

  const options = {
      elements: {
        point: {
          radius: 0
        }
      },
      plugins: {
        title: {
          display: true,
          text: stock.symbol + ' Stocks Over the Last ' + capitalise(type)
        },
        annotation: {
          annotations: [{
            type: 'line',
            yMin: minimum,
            yMax: minimum,
            borderColor: 'rgb(200, 50, 50)',
            borderWidth: 1,
            borderDash: [10, 5]
          },
          {
            type: 'line',
            yMin: maximum,
            yMax: maximum,
            borderColor: 'rgb(200, 50, 50)',
            borderWidth: 1,
            borderDash: [10, 5]
          },
          {
            type: 'line',
            yMin: mean,
            yMax: mean,
            borderColor: 'rgb(50, 150, 50)',
            borderWidth: 1,
            borderDash: [10, 5]
          }]
        }
      }
    } as ChartOptions<"line">;

  return <Line data={data} options={options} />
}
