import React, { createContext, useContext, useState, ReactNode } from "react";

interface UploadContextType {
  file: File | null;
  setFile: (file: File | null) => void;
  clearFile: () => void; // <-- Add the clearFile function here
}

const UploadContext = createContext<UploadContextType | undefined>(undefined);

export const UploadProvider = ({ children }: { children: ReactNode }) => {
  const [file, setFile] = useState<File | null>(null);

  // Define the function that sets the file to null
  const clearFile = () => {
    setFile(null);
  };

  return (
    // Provide the new clearFile function to the rest of the app
    <UploadContext.Provider value={{ file, setFile, clearFile }}>
      {children}
    </UploadContext.Provider>
  );
};

export const useUpload = () => {
  const context = useContext(UploadContext);
  if (context === undefined) {
    throw new Error("useUpload must be used within an UploadProvider");
  }
  return context;
};
