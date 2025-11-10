
export interface EmotionPrediction {
  id: string;
  timestamp: Date;
  text: string;
  emotion: string;
  intensity: number;
  source: string;
}

/**
 * Converts an array of emotion predictions to CSV format
 */
export function convertToCSV(predictions: EmotionPrediction[]): string {
  // Create CSV header
  const headers = ['Text', 'Emotion', 'Intensity', 'Timestamp'];
  
  // Create CSV rows
  const rows = predictions.map(prediction => [
    `"${prediction.text.replace(/"/g, '""')}"`, // Escape quotes in text
    prediction.emotion,
    prediction.intensity.toString(),
    new Date(prediction.timestamp).toISOString(),
  ]);
  
  // Combine headers and rows
  return [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n');
}

/**
 * Generates a downloadable CSV file from prediction data
 */
export function downloadCSV(predictions: EmotionPrediction[], filename = 'emotion-predictions.csv'): void {
  const csv = convertToCSV(predictions);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
