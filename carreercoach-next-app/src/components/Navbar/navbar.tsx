"use client";
import React from "react";
import {
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  Link,
  Button,
} from "@nextui-org/react";
import type { NextRouter } from "next/router";
import { redirect } from "next/navigation";
import { signOut } from "next-auth/react";
import { getClientSession } from "@/hooks/getClientSession";

function NavigationBar() {
  const session = getClientSession();
  return (
    <Navbar>
      <NavbarBrand>
        <p className="font-bold text-inherit">AI Coach</p>
      </NavbarBrand>
      <NavbarContent justify="end">
        {!session?.user ? (
          <>
            <NavbarItem className="hidden lg:flex">
              <Link href="/signin">Login</Link>
            </NavbarItem>
            <NavbarItem>
              <Button as={Link} color="primary" href="/signup" variant="flat">
                Sign Up
              </Button>
            </NavbarItem>
          </>
        ) : (
          <NavbarItem>
            <Button
              color="primary"
              variant="flat"
              onClick={async () => {
                await signOut();
              }}
            >
              Logout
            </Button>
          </NavbarItem>
        )}
      </NavbarContent>
    </Navbar>
  );
}
export default NavigationBar;
