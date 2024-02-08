export interface IErrorCardProps {
  messages: string[];
}

export default function ErrorCard(props: IErrorCardProps) {
  return (
    <div className="error-card">
      {props.messages.map(message => <span>{message}</span>)}
    </div>
  );
}
