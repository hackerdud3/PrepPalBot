"use client";
import React, { useEffect } from "react";
import {
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  Link,
  Button,
} from "@nextui-org/react";
import type { NextRouter } from "next/router";

function NavigationBar() {
  const showButtons = true;

  return (
    <Navbar>
      <NavbarBrand>
        <p className="font-bold text-inherit">AI Coach</p>
      </NavbarBrand>
      <NavbarContent justify="end">
        {showButtons && (
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
        )}
        <NavbarItem>
          <Button color="primary" variant="flat">
            Logout
          </Button>
        </NavbarItem>
      </NavbarContent>
    </Navbar>
  );
}
export default NavigationBar;
