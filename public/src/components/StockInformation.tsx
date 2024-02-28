import IStock, {extractStockData, StockViewType} from "../types/IStock";
import {useEffect, useRef, useState} from "react";
import {ICompany} from "../types/ICompany";
import {capitalise, createDateArray, formatDate, formatDateTime, formatNumber} from "../util";
import {Chart} from "chart.js";
import "chart.js/auto";

import "styles/stock-information.scss";

interface IProps {
  company: ICompany;
  stock: IStock;
}

export const StockInformation = ({ stock, company }: IProps) => {
  const [stockViewType, setStockViewType] = useState<StockViewType>("day");
  const [chart, setChart] = useState<Chart | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    // Initialise chart and stock data
    setStockViewType("day");

    // Cleanup chart on dismount
    return () => {
      chart?.destroy();
    };
  }, []);

  // Update chart when `stockViewType` changes
  useEffect(() => {
    if (canvasRef.current) {
      chart?.destroy();

      const newChart = generateLineGraph(canvasRef.current, stock, stockViewType);
      setChart(newChart);
    }
  }, [stockViewType]);

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
      <canvas id={'stock-graph'} ref={canvasRef} />
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
function generateLineGraph(canvas: HTMLCanvasElement, stock: IStock, type: StockViewType) {
  const stockData = extractStockData(stock, type);

  return new Chart(canvas, {
    type: 'line',
    data: {
      labels: createDateArray(...stockTypeToDates(type), stockData.length).map(type === "day" ? formatDateTime : formatDate),
      datasets: [
        {
          label: stock.symbol,
          data: stockData
        }
      ]
    },
    options: {
      elements: {
        point: {
          radius: 0
        }
      },
      plugins: {
          title: {
              display: true,
              text: stock.symbol + ' Stocks Over the Last ' + capitalise(type)
          }
      }
    }
  });
}
