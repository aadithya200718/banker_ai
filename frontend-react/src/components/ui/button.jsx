import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow-lg hover:shadow-2xl hover:shadow-primary/50 dark:shadow-xl dark:shadow-primary/30 dark:hover:shadow-2xl dark:hover:shadow-primary/60 hover:scale-105 active:scale-95 transition-all duration-200",
        destructive:
          "bg-destructive text-destructive-foreground shadow-lg hover:shadow-2xl hover:shadow-destructive/50 dark:shadow-xl dark:shadow-destructive/30 dark:hover:shadow-2xl dark:hover:shadow-destructive/60 hover:scale-105 active:scale-95 transition-all duration-200",
        outline:
          "border-2 border-input bg-background shadow-md hover:bg-accent hover:text-accent-foreground hover:border-primary hover:shadow-xl hover:shadow-primary/20 dark:border-primary/50 dark:hover:border-primary dark:hover:shadow-xl dark:hover:shadow-primary/40 hover:scale-105 active:scale-95 transition-all duration-200",
        secondary:
          "bg-secondary text-secondary-foreground shadow-md hover:shadow-xl hover:shadow-secondary/30 dark:shadow-lg dark:hover:shadow-xl dark:hover:shadow-secondary/40 hover:scale-105 active:scale-95 transition-all duration-200",
        ghost:
          "hover:bg-accent hover:text-accent-foreground hover:shadow-md dark:hover:shadow-lg hover:scale-105 active:scale-95 transition-all duration-200",
        link: "text-primary underline-offset-4 hover:underline hover:text-primary/80 transition-all duration-200",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

const Button = React.forwardRef(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
