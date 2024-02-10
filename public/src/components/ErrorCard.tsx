export interface IProps {
  messages: string[];
}

export const ErrorCard = ({ messages }: IProps) => {
  return (
    <div className="error-card">
      {messages.map(message => <span key={message}>{message}</span>)}
    </div>
  );
};

export default ErrorCard;
