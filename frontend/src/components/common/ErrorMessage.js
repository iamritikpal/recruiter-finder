import React from "react";
import "./ErrorMessage.css";

const ErrorMessage = ({ title, message, onRetry }) => {
  return (
    <div className="error-container">
      <h3>{title}</h3>
      <p>{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="retry-btn">
          🔄 Try Again
        </button>
      )}
    </div>
  );
};

export default ErrorMessage;
