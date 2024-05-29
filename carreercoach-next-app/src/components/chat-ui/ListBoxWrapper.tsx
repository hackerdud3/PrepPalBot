import React from "react";

export const ListBoxWrapper = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="w-[900px] h-[80vh] border-small px-1 py-2 rounded-small border-default-200 dark:border-default-100">
      {children}
    </div>
  );
};
