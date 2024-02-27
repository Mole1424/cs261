import IStock from "../types/IStock";

export const StockInformation = ({ stock }: { stock: IStock }) => {
  return <div className={'stock-information'} data-company-id={stock.companyId}>
    TODO
  </div>
};

export default StockInformation;
