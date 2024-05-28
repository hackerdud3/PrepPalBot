import SideNav from "@/components/navbar/side-nav";
import ChatField from "@/components/chat-ui/ChatField";
import React from "react";

interface ChatIdParams {
  id: string;
}
type Props = {
  params: ChatIdParams;
};

const page = (props: Props) => {
  return (
    <div className="flex px-24 gap-8 relative h-full">
      <SideNav />
      <div>
        <ChatField chatId={props.params.id} />
      </div>
    </div>
  );
};
export default page;
