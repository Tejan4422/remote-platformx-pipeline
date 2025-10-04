// React Hooks for API Integration
// This file should be placed in your frontend at: src/hooks/useAPI.ts

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient, type APIResponse, type UploadResponse, type QueryRequest, type GenerateResponsesRequest } from '@/lib/api-client';
import { toast } from '@/hooks/use-toast';

// ============================================================================
// Query Hooks (GET requests)
// ============================================================================

export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000, // Check every 30 seconds
    retry: 3,
  });
};

export const useVectorStoreStatus = () => {
  return useQuery({
    queryKey: ['vectorStore', 'status'],
    queryFn: () => apiClient.getVectorStoreStatus(),
    refetchInterval: 10000, // Check every 10 seconds
  });
};

export const useVectorStoreStats = () => {
  return useQuery({
    queryKey: ['vectorStore', 'stats'],
    queryFn: () => apiClient.getVectorStoreStats(),
    refetchInterval: 30000,
  });
};

export const useRequirements = (sessionId: string | null) => {
  return useQuery({
    queryKey: ['requirements', sessionId],
    queryFn: () => apiClient.getRequirements(sessionId!),
    enabled: !!sessionId,
  });
};

export const useResponses = (sessionId: string | null) => {
  return useQuery({
    queryKey: ['responses', sessionId],
    queryFn: () => apiClient.getResponses(sessionId!),
    enabled: !!sessionId,
  });
};

// ============================================================================
// Mutation Hooks (POST, PUT, DELETE requests)
// ============================================================================

export const useUploadRFP = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (file: File) => apiClient.uploadRFP(file),
    onSuccess: (data: UploadResponse) => {
      toast({
        title: "Upload Successful",
        description: `Extracted ${data.requirements.length} requirements from ${data.file_info.filename}`,
      });
      
      // Invalidate and refetch requirements
      queryClient.invalidateQueries({ queryKey: ['requirements', data.session_id] });
    },
    onError: (error: Error) => {
      toast({
        title: "Upload Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

export const useDirectQuery = () => {
  return useMutation({
    mutationFn: (query: QueryRequest) => apiClient.directQuery(query),
    onSuccess: (data: APIResponse) => {
      toast({
        title: "Query Successful",
        description: `Quality Score: ${data.data?.quality_score || 'N/A'}`,
      });
    },
    onError: (error: Error) => {
      toast({
        title: "Query Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

export const useGenerateResponses = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (request: GenerateResponsesRequest) => apiClient.generateResponses(request),
    onSuccess: (data: APIResponse, variables: GenerateResponsesRequest) => {
      const summary = data.data?.summary;
      toast({
        title: "Response Generation Complete",
        description: `Generated ${summary?.successful_responses || 0}/${summary?.total_requirements || 0} responses`,
      });
      
      // Invalidate and refetch responses
      queryClient.invalidateQueries({ queryKey: ['responses', variables.session_id] });
    },
    onError: (error: Error) => {
      toast({
        title: "Response Generation Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

export const useIndexRFPResponses = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (file: File) => apiClient.indexRFPResponses(file),
    onSuccess: (data: APIResponse) => {
      toast({
        title: "Indexing Successful",
        description: `Added ${data.data?.indexing_results?.documents_added || 0} documents to knowledge base`,
      });
      
      // Invalidate vector store stats
      queryClient.invalidateQueries({ queryKey: ['vectorStore'] });
    },
    onError: (error: Error) => {
      toast({
        title: "Indexing Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

export const useUploadHistoricalData = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ files, description }: { files: File[]; description?: string }) => 
      apiClient.uploadHistoricalData(files, description),
    onSuccess: (data: APIResponse) => {
      toast({
        title: "Historical Data Upload Successful",
        description: `Processed ${data.data?.summary?.total_documents_added || 0} documents`,
      });
      
      // Invalidate vector store stats
      queryClient.invalidateQueries({ queryKey: ['vectorStore'] });
    },
    onError: (error: Error) => {
      toast({
        title: "Historical Data Upload Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

export const useCleanupSession = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (sessionId: string) => apiClient.cleanupSession(sessionId),
    onSuccess: (data: APIResponse, sessionId: string) => {
      toast({
        title: "Session Cleaned Up",
        description: "Session data and temporary files have been removed",
      });
      
      // Remove session-related queries from cache
      queryClient.removeQueries({ queryKey: ['requirements', sessionId] });
      queryClient.removeQueries({ queryKey: ['responses', sessionId] });
    },
    onError: (error: Error) => {
      toast({
        title: "Cleanup Failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });
};

// ============================================================================
// Custom Session Management Hook
// ============================================================================

export const useSession = () => {
  const queryClient = useQueryClient();
  
  const clearSession = (sessionId: string) => {
    queryClient.removeQueries({ queryKey: ['requirements', sessionId] });
    queryClient.removeQueries({ queryKey: ['responses', sessionId] });
  };
  
  const refreshSession = (sessionId: string) => {
    queryClient.invalidateQueries({ queryKey: ['requirements', sessionId] });
    queryClient.invalidateQueries({ queryKey: ['responses', sessionId] });
  };
  
  return {
    clearSession,
    refreshSession,
  };
};