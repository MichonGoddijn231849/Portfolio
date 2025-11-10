import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  className?: string;
}

export const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelect, className }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    // We only handle a single file upload
    if (acceptedFiles.length > 0) {
      onFileSelect(acceptedFiles[0]);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.webm'],
      'audio/*': ['.mp3', '.wav', 'm4a'],
      'text/csv': ['.csv'],
      'text/plain': ['.txt'],
    },
    multiple: false,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "relative block w-full rounded-lg border-2 border-dashed border-muted bg-white/5 p-12 text-center transition-all duration-300 hover:border-primary/60 cursor-pointer",
        {
          'border-primary bg-primary/10 ring-2 ring-primary/40': isDragActive,
        },
        className
      )}
    >
      <input {...getInputProps()} />
      
      <div className="flex flex-col items-center justify-center gap-4 text-muted-foreground">
        <UploadCloud className={cn("h-12 w-12", isDragActive && "text-primary animate-bounce")} />
        <p className="text-lg font-semibold">
          {isDragActive ? "Drop your file to begin!" : "Drag & drop your file here"}
        </p>
        <p className="text-sm">or click to browse</p>
        <p className="text-xs mt-4">(MP4, MP3, WAV, CSV, TXT)</p>
      </div>
    </div>
  );
};
