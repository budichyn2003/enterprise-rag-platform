import React from "react";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    interactive?: boolean;
    padding?: "none" | "sm" | "md" | "lg";
}

export const Card: React.FC<CardProps> = ({
    children,
    interactive = false,
    padding = "md",
    className = "",
    ...props
}) => {
    const baseStyles = "glass-panel rounded-xl";

    const paddings = {
        none: "p-0",
        sm: "p-4",
        md: "p-6",
        lg: "p-8",
    };

    const interactiveStyles = interactive
        ? "transition duration-200 hover:-translate-y-0.5 hover:shadow-md cursor-pointer"
        : "";

    return (
        <div className={`${baseStyles} ${paddings[padding]} ${interactiveStyles} ${className}`} {...props}>
            {children}
        </div>
    );
};