// Enhanced DocumentUpload Component with API Integration
// This replaces your existing src/components/DocumentUpload.tsx

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, FileText, AlertCircle, CheckCircle2, File, Loader2 } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { useUploadRFP, useVectorStoreStatus } from "@/hooks/useAPI";

export const DocumentUpload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  // API hooks
  const uploadMutation = useUploadRFP();
  const { data: vectorStoreStatus } = useVectorStoreStatus();
  
  const isLoading = uploadMutation.isPending;
  const uploadedFile = uploadMutation.data?.file_info;
  const requirements = uploadMutation.data?.requirements;

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleFileUpload = (file: File) => {
    // Validate file type
    const allowedTypes = ['.pdf', '.docx', '.xlsx', '.xls'];
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      return; // Error will be handled by mutation
    }

    uploadMutation.mutate(file, {
      onSuccess: (data) => {
        setSessionId(data.session_id);
      }
    });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Vector Store Status */}
      <Card className="border-l-4 border-l-primary">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {vectorStoreStatus?.data?.ready_for_queries ? (
                <CheckCircle2 className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-yellow-500" />
              )}
              <div>
                <p className="font-medium">Knowledge Base Status</p>
                <p className="text-sm text-muted-foreground">
                  {vectorStoreStatus?.data?.total_documents || 0} documents indexed
                </p>
              </div>
            </div>
            <Badge variant={vectorStoreStatus?.data?.ready_for_queries ? "default" : "secondary"}>
              {vectorStoreStatus?.data?.ready_for_queries ? "Ready" : "Not Ready"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Upload Area */}
      <Card className="border-2 border-dashed transition-colors" 
            style={{ 
              borderColor: isDragging ? "hsl(var(--primary))" : "hsl(var(--border))",
              backgroundColor: isDragging ? "hsl(var(--primary) / 0.05)" : "transparent"
            }}>
        <CardHeader>
          <CardTitle>Upload RFP Document</CardTitle>
          <CardDescription>
            Drag and drop your RFP document or click to browse. Supports PDF, DOCX, and Excel formats.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className="border-2 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer hover:bg-muted/50"
            onClick={() => !isLoading && document.getElementById('fileInput')?.click()}
          >
            {isLoading ? (
              <Loader2 className="h-12 w-12 mx-auto mb-4 text-primary animate-spin" />
            ) : (
              <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            )}
            
            <p className="text-lg font-medium mb-2">
              {isLoading ? "Processing document..." : "Drop your RFP document here"}
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              {isLoading ? "Extracting requirements..." : "or click to browse files"}
            </p>
            
            {!isLoading && (
              <div className="flex justify-center gap-2">
                <Badge variant="secondary">PDF</Badge>
                <Badge variant="secondary">DOCX</Badge>
                <Badge variant="secondary">XLSX</Badge>
              </div>
            )}
            
            <input
              id="fileInput"
              type="file"
              className="hidden"
              accept=".pdf,.docx,.xlsx,.xls"
              onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
              disabled={isLoading}
            />
          </div>

          {/* Upload Result */}
          {uploadedFile && requirements && (
            <Alert className="mt-4">
              <CheckCircle2 className="h-4 w-4 text-success" />
              <AlertDescription className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Successfully processed {uploadedFile.filename}</p>
                  <p className="text-sm text-muted-foreground">Session ID: {sessionId}</p>
                </div>
                <Badge>{requirements.length} requirements found</Badge>
              </AlertDescription>
            </Alert>
          )}

          {/* Error State */}
          {uploadMutation.isError && (
            <Alert className="mt-4" variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {uploadMutation.error?.message || "Failed to process document"}
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Sample Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <File className="h-5 w-5" />
            Sample Templates
          </CardTitle>
          <CardDescription>
            Download our sample RFP templates to get started quickly
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <Button variant="outline" className="w-full justify-start">
              <FileText className="h-4 w-4 mr-2" />
              IT Services RFP
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <FileText className="h-4 w-4 mr-2" />
              Consulting RFP
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <FileText className="h-4 w-4 mr-2" />
              Software RFP
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};