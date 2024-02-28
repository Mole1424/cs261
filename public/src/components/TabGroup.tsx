import {useState} from "react";

import "styles/tabs.scss"

export interface IProps {
  tabs: ITab[];
  selected?: number; // Default select?
}

export interface ITab {
  label: string;
  onClick?: () => Promise<void | {
    select: boolean;  // Whether to select the current tab
  }>;
}

export const TabGroup = ({ tabs, selected: defaultTabIndex }: IProps) => {
  // TODO select bug
  const [selected, setSelected] = useState(defaultTabIndex ?? -1);

  /** Handle the click of the tab at the given index */
  const handleClick = async (index: number) => {
    const tab = tabs[index];

    // Clickable?
    if (tab.onClick) {
     const returnData = await tab.onClick();

      if (returnData && returnData.select) {
        setSelected(index);
      }
    }
  };

  return (
    <nav className="tab-group">
      {tabs.map(({ label, onClick }, idx) =>
        <div
          className="tab"
          key={label}
          onClick={() => void handleClick(idx)}
          data-selected={selected === idx}
          data-clickable={onClick != undefined}
        >{label}</div>
      )}
    </nav>
  );
};

export default TabGroup;
