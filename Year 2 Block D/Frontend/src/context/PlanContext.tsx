import React, { createContext, useState, useContext, ReactNode } from 'react';

// Define the shape of the context data
interface PlanContextType {
  selectedPlan: string;
  setSelectedPlan: (plan: string) => void;
}

// Create the context with a default value
const PlanContext = createContext<PlanContextType | undefined>(undefined);

// Create the provider component that will wrap your app
export const PlanProvider = ({ children }: { children: ReactNode }) => {
  const [selectedPlan, setSelectedPlan] = useState("Starter"); // Default to Starter plan

  return (
    <PlanContext.Provider value={{ selectedPlan, setSelectedPlan }}>
      {children}
    </PlanContext.Provider>
  );
};

// Create a custom hook for easy access to the context
export const usePlan = () => {
  const context = useContext(PlanContext);
  if (context === undefined) {
    throw new Error('usePlan must be used within a PlanProvider');
  }
  return context;
};
