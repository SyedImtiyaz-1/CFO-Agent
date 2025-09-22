import React, { ReactNode, FC, ChangeEvent } from 'react';

// Card Components
interface CardProps {
  children: ReactNode;
  className?: string;
}

export const Card: FC<CardProps> = ({ children, className = '' }) => (
  <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
    {children}
  </div>
);

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

export const CardHeader: FC<CardHeaderProps> = ({ children, className = '' }) => (
  <div className={`border-b pb-4 mb-4 ${className}`}>
    {children}
  </div>
);

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

export const CardTitle: FC<CardTitleProps> = ({ children, className = '' }) => (
  <h3 className={`text-lg font-medium ${className}`}>
    {children}
  </h3>
);

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export const CardContent: FC<CardContentProps> = ({ children, className = '' }) => (
  <div className={className}>
    {children}
  </div>
);

// Button Component
interface ButtonProps {
  children: ReactNode;
  onClick?: () => void;
  className?: string;
  disabled?: boolean;
  variant?: 'default' | 'outline' | 'destructive';
  size?: 'default' | 'sm' | 'lg';
  type?: 'button' | 'submit' | 'reset';
}

export const Button: FC<ButtonProps> = ({
  children,
  onClick,
  className = '',
  disabled = false,
  variant = 'default',
  size = 'default',
  type = 'button'
}) => {
  const baseStyles = 'rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors';
  const variantStyles = {
    default: 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500',
    outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-indigo-500',
    destructive: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  };
  const sizeStyles = {
    default: 'px-4 py-2 text-sm',
    sm: 'px-3 py-1.5 text-xs',
    lg: 'px-6 py-3 text-base',
  };
  
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      } ${className}`}
    >
      {children}
    </button>
  );
};

// Input Component
interface InputProps {
  id?: string;
  type?: string;
  value?: string | number;
  onChange?: (e: ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

export const Input: FC<InputProps> = ({ 
  id, 
  type = 'text', 
  value, 
  onChange, 
  placeholder, 
  className = '',
  disabled = false
}) => (
  <input
    id={id}
    type={type}
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    disabled={disabled}
    className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm ${
      disabled ? 'bg-gray-100' : ''
    } ${className}`}
  />
);

// Label Component
interface LabelProps {
  htmlFor?: string;
  children: ReactNode;
  className?: string;
  required?: boolean;
}

export const Label: FC<LabelProps> = ({ 
  htmlFor, 
  children, 
  className = '',
  required = false
}) => (
  <label 
    htmlFor={htmlFor} 
    className={`block text-sm font-medium text-gray-700 mb-1 ${className}`}
  >
    {children}
    {required && <span className="text-red-500 ml-1">*</span>}
  </label>
);

// Slider Component
interface SliderProps {
  id?: string;
  min: number;
  max: number;
  step: number;
  value: number[];
  onValueChange: (value: number[]) => void;
  className?: string;
  disabled?: boolean;
}

export const Slider: FC<SliderProps> = ({ 
  id, 
  min, 
  max, 
  step, 
  value, 
  onValueChange, 
  className = '',
  disabled = false
}) => (
  <input
    type="range"
    id={id}
    min={min}
    max={max}
    step={step}
    value={value[0]}
    onChange={(e) => onValueChange([Number(e.target.value)])}
    disabled={disabled}
    className={`w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer ${
      disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
    } ${className}`}
  />
);

// Download Icon Component
interface DownloadIconProps {
  className?: string;
}

export const DownloadIcon: FC<DownloadIconProps> = ({ 
  className = '' 
}) => (
  <svg
    className={`w-5 h-5 ${className}`}
    fill="none"
    stroke="currentColor"
    viewBox="0 0 24 24"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
    />
  </svg>
);

// Toast Hook
export interface ToastMessage {
  title: string;
  description: string;
  variant: 'default' | 'destructive';
}

export const useToast = () => {
  const [toast, setToast] = React.useState<ToastMessage | null>(null);

  const show = (
    title: string, 
    description: string, 
    variant: 'default' | 'destructive' = 'default'
  ) => {
    setToast({ title, description, variant });
    setTimeout(() => setToast(null), 5000);
  };

  return { toast, show };
};

// Toast Component
interface ToastProps {
  title: string;
  description: string;
  variant: 'default' | 'destructive';
  onClose: () => void;
}

export const Toast: FC<ToastProps> = ({ title, description, variant, onClose }) => {
  const bgColor = variant === 'destructive' ? 'bg-red-50' : 'bg-green-50';
  const textColor = variant === 'destructive' ? 'text-red-800' : 'text-green-800';
  const iconColor = variant === 'destructive' ? 'text-red-400' : 'text-green-400';

  return (
    <div className={`rounded-md ${bgColor} p-4 mb-4`}>
      <div className="flex">
        <div className="flex-shrink-0">
          {variant === 'destructive' ? (
            <svg
              className={`h-5 w-5 ${iconColor}`}
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          ) : (
            <svg
              className={`h-5 w-5 ${iconColor}`}
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
          )}
        </div>
        <div className="ml-3">
          <h3 className={`text-sm font-medium ${textColor}`}>{title}</h3>
          <div className={`mt-1 text-sm ${textColor}`}>
            <p>{description}</p>
          </div>
        </div>
        <div className="ml-auto pl-3">
          <div className="-mx-1.5 -my-1.5">
            <button
              type="button"
              onClick={onClose}
              className={`inline-flex ${bgColor} ${textColor} rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                variant === 'destructive' 
                  ? 'focus:ring-red-500 hover:bg-red-100' 
                  : 'focus:ring-green-500 hover:bg-green-100'
              }`}
            >
              <span className="sr-only">Dismiss</span>
              <svg
                className="h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                aria-hidden="true"
              >
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
