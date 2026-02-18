import React from "react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  ScrollText,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const Sidebar = ({ collapsed = false, onToggle }) => {
  const location = useLocation();

  const menuItems = [
    {
      icon: LayoutDashboard,
      label: "Dashboard",
      path: "/dashboard",
      description: "New Verification",
    },
    {
      icon: ScrollText,
      label: "Audit Logs",
      path: "/logs",
      description: "History & Reports",
    },
    {
      icon: Settings,
      label: "Settings",
      path: "/settings",
      description: "Preferences",
    },
  ];

  return (
    <div
      className={cn(
        "relative h-full bg-background border-r border-border transition-all duration-300 flex flex-col",
        collapsed ? "w-16" : "w-64",
      )}
    >
      {/* Toggle Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={onToggle}
        className="absolute -right-3 top-6 z-10 h-6 w-6 rounded-full border bg-background shadow-md hover:shadow-lg"
      >
        {collapsed ? (
          <ChevronRight className="h-3 w-3" />
        ) : (
          <ChevronLeft className="h-3 w-3" />
        )}
      </Button>

      {/* Menu Items */}
      <nav className="flex-1 p-3 space-y-2 mt-4">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link key={item.path} to={item.path}>
              <div
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all group",
                  isActive
                    ? "bg-primary text-primary-foreground shadow-md"
                    : "hover:bg-accent hover:text-accent-foreground",
                )}
              >
                <Icon
                  className={cn(
                    "h-5 w-5 flex-shrink-0",
                    isActive
                      ? "text-primary-foreground"
                      : "text-muted-foreground group-hover:text-foreground",
                  )}
                />
                {!collapsed && (
                  <div className="flex-1 overflow-hidden">
                    <p
                      className={cn(
                        "text-sm font-semibold truncate",
                        isActive ? "text-primary-foreground" : "",
                      )}
                    >
                      {item.label}
                    </p>
                    <p
                      className={cn(
                        "text-xs truncate",
                        isActive
                          ? "text-primary-foreground/80"
                          : "text-muted-foreground",
                      )}
                    >
                      {item.description}
                    </p>
                  </div>
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      {!collapsed && (
        <div className="p-3 border-t border-border">
          <p className="text-xs text-muted-foreground text-center">
            Banker Verify v1.0
          </p>
        </div>
      )}
    </div>
  );
};

export default Sidebar;
