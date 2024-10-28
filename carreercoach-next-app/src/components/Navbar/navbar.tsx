import { getServerSession } from "next-auth";
import { signOut } from "@/auth";
import {
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  Link,
  Button,
  DropdownTrigger,
  Dropdown,
  DropdownMenu,
  DropdownItem,
} from "@nextui-org/react";
import AvatarDropDown from "./AvatarDropDown";

export default async function NavBar() {
  const session = await getServerSession();

  return (
    <Navbar
      isBlurred={false}
      isBordered={false}
      maxWidth="full"
      className="px-14 bg-transparent"
    >
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
          <AvatarDropDown user={session.user} />
        )}
      </NavbarContent>
    </Navbar>
  );
}
