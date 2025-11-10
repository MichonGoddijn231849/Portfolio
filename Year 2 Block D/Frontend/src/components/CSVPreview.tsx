
import React from "react";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow 
} from "@/components/ui/table";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { EmotionPrediction, downloadCSV } from "@/lib/csv-utils";

interface CSVPreviewProps {
  predictions: EmotionPrediction[];
  maxRows?: number;
}

const CSVPreview: React.FC<CSVPreviewProps> = ({ predictions, maxRows = 5 }) => {
  if (!predictions || predictions.length === 0) {
    return null;
  }

  const displayPredictions = predictions.slice(0, maxRows);
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>CSV Output Preview</span>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => downloadCSV(predictions)}
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Download CSV
          </Button>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Text</TableHead>
                <TableHead>Emotion</TableHead>
                <TableHead>Intensity</TableHead>
                <TableHead>Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {displayPredictions.map((prediction) => (
                <TableRow key={prediction.id}>
                  <TableCell className="font-medium max-w-72 truncate">
                    {prediction.text}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {prediction.emotion}
                    </div>
                  </TableCell>
                  <TableCell>{prediction.intensity}%</TableCell>
                  <TableCell>
                    {new Date(prediction.timestamp).toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
      {predictions.length > maxRows && (
        <CardFooter className="text-sm text-muted-foreground">
          Showing {maxRows} of {predictions.length} predictions
        </CardFooter>
      )}
    </Card>
  );
};

export default CSVPreview;
