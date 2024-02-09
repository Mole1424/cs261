import {useState} from "react";

import "styles/tabs.scss"

export interface ITabProps {
  tabs: ITab[];
  selected?: number; // Default select?
}

export interface ITab {
  label: string;
  onClick?: () => Promise<void | {
    select: boolean;  // Whether to select the current tab
  }>;
}

interface ITabState {
  selected: number;  // Index of selected tab, or -1
}

export default function TabGroup(props: ITabProps) {
  const [state, setState] = useState<ITabState>({
    selected: props.selected ?? -1
  });

  /** Handle the click of the tab at the given index */
  const handleClick = async (index: number) => {
    const tab = props.tabs[index];

    // Clickable?
    if (tab.onClick) {
     const returnData = await tab.onClick();

      if (returnData && returnData.select) {
        setState({ selected: index });
      }
    }
  }

  return (
    <nav className="tab-group">
      {props.tabs.map(({ label, onClick }, idx) =>
        <div
          className="tab"
          key={idx}
          onClick={() => void handleClick(idx)}
          data-selected={state.selected === idx}
          data-clickable={onClick != undefined}
        >{label}</div>
      )}
    </nav>
  );
}
