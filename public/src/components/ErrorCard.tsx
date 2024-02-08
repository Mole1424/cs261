import React from "react";

export interface IErrorCardProps {
  messages: string[];
}

export default class ErrorCard extends React.Component<IErrorCardProps, {}> {
  constructor(props: IErrorCardProps) {
    super(props);
  }

  public render() {
    return (
      <div className="error-card">
        {this.props.messages.map(message => <span>{message}</span>)}
      </div>
    );
  }
}
