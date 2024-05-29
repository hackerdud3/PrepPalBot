import { IUser } from "@/lib/models/user.model";
import { Avatar, Chip, Divider } from "@nextui-org/react";
import { useSession } from "next-auth/react";
import React from "react";

type Props = {
  message: string;
  sender: string;
};

const MessageChip = (props: Props) => {
  const { data: session, status } = useSession();
  const userName = session?.user?.name ?? "Guest";
  return (
    <div className="p-2 my-10 flex justify-start items-start gap-4 ">
      <div>
        <Avatar name={userName} />
      </div>

      <span className="mt-[8px]">{props.message}</span>
    </div>
  );
};

export default MessageChip;
