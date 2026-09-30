import React from "react";

type ButtonVariant = "primary" | "secondary" | "glass" | "outline" | "danger";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: ButtonVariant;
    size?: ButtonSize;
}

export const Button: React.FC<ButtonProps> = ({
    children,
    variant = "primary",
    size = "md",
    className = "",
    ...props
}) => {
    const baseStyles = "inline-flex items-center justify-center rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-mc-primary/50 disabled:opacity-50 disabled:cursor-not-allowed font-medium";

    const variants = {
        primary: "bg-mc-primary text-white hover:bg-mc-dark",
        secondary: "bg-mc-soft text-mc-dark hover:bg-white",
        glass: "glass-panel text-mc-dark hover:bg-white/60",
        outline: "border border-mc-primary text-mc-primary hover:bg-mc-primary hover:text-white",
        danger: "bg-error text-white hover:bg-red-600",
    };

    const sizes = {
        sm: "px-3 py-1.5 text-sm",
        md: "px-4 py-2 text-base",
        lg: "px-6 py-3 text-lg",
    };

    const combinedClassName = `${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`;

    return (
        <button className={combinedClassName} {...props}>
            {children}
        </button>
    );
};