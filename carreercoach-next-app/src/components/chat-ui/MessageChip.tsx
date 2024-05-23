import React from "react";

type Props = {};

const message = (props: Props) => {
  const [message, setMessage] = React.useState([]);

  message.join("hello ");
  return (
    <div>
      <p>Hello</p>
    </div>
  );
};

export default message;
