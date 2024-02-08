import React from "react";
import "styles/tabs.scss"

export interface ITabProps {
  tabs: ITab[];
}

export interface ITab {
  label: string;
  onClick?: () => Promise<{
    select: boolean;  // Whether to select the current tab
  }>;
}

interface ITabState {
  selected: number;  // Index of selected tab, or -1
}

export default class TabGroup extends React.Component<ITabProps, ITabState> {
  constructor(props: ITabProps) {
    super(props);
    this.state = {
      selected: -1
    };
  }

  /** Handle the click of the tab at the given index */
  private async handleClick(index: number) {
    const tab = this.props.tabs[index];

    // Clickable?
    if (tab.onClick) {
     const returnData = await tab.onClick();

      if (returnData.select) {
        this.setState({ selected: index });
      }
    }
  }

  public render() {
    return (
      <nav className="tab-group">
        {this.props.tabs.map(({ label, onClick }, idx) =>
          <div
            className="tab"
            key={idx}
            onClick={() => this.handleClick.bind(this)(idx)}
            data-selected={this.state.selected === idx}
            data-clickable={onClick != undefined}
          >{label}</div>
        )}
      </nav>
    );
  }
}
