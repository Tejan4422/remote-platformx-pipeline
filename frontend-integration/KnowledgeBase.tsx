// Enhanced KnowledgeBase Component with API Integration
// This replaces your existing src/components/KnowledgeBase.tsx

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Database, Upload, CheckCircle2, FileText, TrendingUp, Loader2, AlertCircle } from "lucide-react";
import { useIndexRFPResponses, useUploadHistoricalData, useVectorStoreStats } from "@/hooks/useAPI";

export const KnowledgeBase = () => {
  const [isDragging, setIsDragging] = useState(false);
  
  // API hooks
  const indexMutation = useIndexRFPResponses();
  const uploadHistoricalMutation = useUploadHistoricalData();
  const { data: vectorStoreStats, isLoading: statsLoading } = useVectorStoreStats();

  const stats = vectorStoreStats?.data;
  const isUploading = indexMutation.isPending || uploadHistoricalMutation.isPending;

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
    const files = Array.from(e.dataTransfer.files);
    handleMultipleFileUpload(files);
  };

  const handleSingleFileUpload = (file: File) => {
    // For single file indexing (RFP responses)
    indexMutation.mutate(file);
  };

  const handleMultipleFileUpload = (files: File[]) => {
    // For multiple file upload (historical data)
    if (files.length === 1) {
      handleSingleFileUpload(files[0]);
    } else {
      uploadHistoricalMutation.mutate({ 
        files, 
        description: `Batch upload of ${files.length} files` 
      });
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Statistics Overview */}
      <div className="grid md:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total Documents</CardDescription>
            <CardTitle className="text-3xl">
              {statsLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                stats?.vector_store?.total_documents || 0
              )}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Vector Dimension</CardDescription>
            <CardTitle className="text-3xl">
              {stats?.vector_store?.vector_dimension || 0}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Index Status</CardDescription>
            <CardTitle className="text-3xl flex items-center gap-2">
              {stats?.vector_store?.exists ? (
                <>
                  <CheckCircle2 className="h-6 w-6 text-success" />
                  Live
                </>
              ) : (
                <>
                  <AlertCircle className="h-6 w-6 text-warning" />
                  Empty
                </>
              )}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Storage Size</CardDescription>
            <CardTitle className="text-3xl">
              {stats?.storage_summary?.total_size_mb?.toFixed(1) || 0} MB
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Upload Area */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Upload Historical RFP Responses
              </CardTitle>
              <CardDescription>
                Add your past successful proposals to improve AI response quality
              </CardDescription>
            </div>
            <Button 
              className="gap-2" 
              onClick={() => document.getElementById('fileInput')?.click()}
              disabled={isUploading}
            >
              {isUploading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Upload className="h-4 w-4" />
              )}
              Upload Documents
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div 
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragging 
                ? 'border-primary bg-primary/5' 
                : 'border-muted-foreground/25 hover:border-muted-foreground/50'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {isUploading ? (
              <>
                <Loader2 className="h-12 w-12 mx-auto mb-4 text-primary animate-spin" />
                <p className="text-lg font-medium mb-2">Processing documents...</p>
                <p className="text-sm text-muted-foreground mb-4">
                  {indexMutation.isPending ? "Indexing RFP responses" : "Uploading historical data"}
                </p>
              </>
            ) : (
              <>
                <Database className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-lg font-medium mb-2">Build Your Knowledge Base</p>
                <p className="text-sm text-muted-foreground mb-4">
                  Upload past RFP responses, case studies, and company documentation
                </p>
                <div className="flex justify-center gap-2">
                  <Badge variant="secondary">Excel (.xlsx)</Badge>
                  <Badge variant="secondary">Multiple files supported</Badge>
                </div>
              </>
            )}
            
            <input
              id="fileInput"
              type="file"
              className="hidden"
              accept=".xlsx,.xls"
              multiple
              onChange={(e) => {
                const files = Array.from(e.target.files || []);
                if (files.length > 0) {
                  handleMultipleFileUpload(files);
                }
              }}
              disabled={isUploading}
            />
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Document Processing Status</CardTitle>
          <CardDescription>
            Recent uploads and processing activity
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Success State */}
            {indexMutation.isSuccess && (
              <div className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <div className="flex-1">
                  <p className="font-medium text-green-900">Successfully indexed RFP responses</p>
                  <p className="text-sm text-green-700">
                    Added {indexMutation.data?.data?.indexing_results?.documents_added || 0} new documents
                  </p>
                </div>
                <Badge variant="outline" className="text-green-700 border-green-300">
                  Complete
                </Badge>
              </div>
            )}

            {uploadHistoricalMutation.isSuccess && (
              <div className="flex items-center gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <div className="flex-1">
                  <p className="font-medium text-green-900">Historical data upload complete</p>
                  <p className="text-sm text-green-700">
                    Processed {uploadHistoricalMutation.data?.data?.upload_info?.successful_files || 0} files
                  </p>
                </div>
                <Badge variant="outline" className="text-green-700 border-green-300">
                  Complete
                </Badge>
              </div>
            )}

            {/* Loading State */}
            {isUploading && (
              <div className="flex items-center gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
                <div className="flex-1">
                  <p className="font-medium text-blue-900">Processing documents...</p>
                  <Progress value={45} className="mt-2" />
                </div>
                <Badge variant="outline" className="text-blue-700 border-blue-300">
                  Processing
                </Badge>
              </div>
            )}

            {/* Error State */}
            {(indexMutation.isError || uploadHistoricalMutation.isError) && (
              <div className="flex items-center gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="h-5 w-5 text-red-600" />
                <div className="flex-1">
                  <p className="font-medium text-red-900">Upload failed</p>
                  <p className="text-sm text-red-700">
                    {indexMutation.error?.message || uploadHistoricalMutation.error?.message}
                  </p>
                </div>
                <Badge variant="outline" className="text-red-700 border-red-300">
                  Failed
                </Badge>
              </div>
            )}

            {/* Default State */}
            {!isUploading && !indexMutation.isSuccess && !uploadHistoricalMutation.isSuccess && !indexMutation.isError && !uploadHistoricalMutation.isError && (
              <div className="text-center py-8 text-muted-foreground">
                <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No recent activity</p>
                <p className="text-sm">Upload documents to get started</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Capabilities */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            System Capabilities
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <div className={`p-4 rounded-lg border ${stats?.capabilities?.ready_for_queries ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className={`h-4 w-4 ${stats?.capabilities?.ready_for_queries ? 'text-green-600' : 'text-gray-400'}`} />
                <span className="font-medium">Query Ready</span>
              </div>
              <p className="text-sm text-muted-foreground">
                {stats?.capabilities?.ready_for_queries ? 'System ready for queries' : 'Upload documents first'}
              </p>
            </div>

            <div className={`p-4 rounded-lg border ${stats?.capabilities?.supports_similarity_search ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className={`h-4 w-4 ${stats?.capabilities?.supports_similarity_search ? 'text-green-600' : 'text-gray-400'}`} />
                <span className="font-medium">Similarity Search</span>
              </div>
              <p className="text-sm text-muted-foreground">
                {stats?.capabilities?.supports_similarity_search ? 'Vector search enabled' : 'Not available'}
              </p>
            </div>

            <div className={`p-4 rounded-lg border ${stats?.capabilities?.can_add_documents ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'}`}>
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle2 className={`h-4 w-4 ${stats?.capabilities?.can_add_documents ? 'text-green-600' : 'text-gray-400'}`} />
                <span className="font-medium">Document Upload</span>
              </div>
              <p className="text-sm text-muted-foreground">
                {stats?.capabilities?.can_add_documents ? 'Ready to add documents' : 'Upload disabled'}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};