import React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { LogOut, ShieldCheck } from "lucide-react";
import { ModeToggle } from "./ModeToggle";

function Header({ user, onLogout }) {
  // Get initials from name
  const getInitials = (name) => {
    if (!name) return "BK";
    return name
      .split(" ")
      .map((n) => n[0])
      .slice(0, 2)
      .join("")
      .toUpperCase();
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <div className="hidden md:block">
            <h1 className="text-xl font-bold tracking-tight text-foreground">
              Banker Verify
            </h1>
            <p className="text-xs font-medium text-muted-foreground">
              Identity Assurance Platform
            </p>
          </div>
        </div>

        {/* User Profile & Actions */}
        <div className="flex items-center gap-4">
          <div className="hidden text-right sm:block">
            <p className="text-sm font-semibold leading-none">
              {user?.name || "Banker"}
            </p>
            <p className="text-xs text-muted-foreground">
              {user?.branchId ? `Branch ${user.branchId}` : "HQ"}
            </p>
          </div>
          <Avatar className="h-9 w-9 border-2 border-background ring-2 ring-muted transition-transform hover:scale-105">
            <AvatarImage
              src={`https://api.dicebear.com/7.x/initials/svg?seed=${user?.name || "User"}`}
            />
            <AvatarFallback className="bg-primary text-primary-foreground">
              {getInitials(user?.name)}
            </AvatarFallback>
          </Avatar>
          <ModeToggle />
          <Button
            variant="ghost"
            size="icon"
            onClick={onLogout}
            className="text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
            title="Safe Logout"
          >
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  );
}

export default Header;
