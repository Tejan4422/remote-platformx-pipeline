// API Client for RFP Response Generator Frontend
// This file should be placed in your frontend at: src/lib/api-client.ts

export interface APIResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  session_id?: string;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  session_id: string;
  requirements: string[];
  extraction_metadata?: any;
  file_info: {
    filename: string;
    size: string | number;
    type: string;
    extension: string;
  };
}

export interface QueryRequest {
  query: string;
  top_k?: number;
  model?: string;
}

export interface GenerateResponsesRequest {
  requirements: string[];
  top_k?: number;
  model?: string;
  session_id: string;
}

export interface Requirement {
  requirement_index: number;
  requirement: string;
  answer?: string;
  quality_score?: number;
  quality_status?: string;
  status: 'success' | 'error';
  error?: string;
}

export interface VectorStoreStats {
  vector_store: {
    exists: boolean;
    path: string;
    total_documents: number;
    vector_dimension: number;
    index_size: number;
  };
  file_statistics: any;
  storage_summary: {
    total_size_bytes: number;
    total_size_mb: number;
    files_count: number;
  };
  capabilities: {
    ready_for_queries: boolean;
    supports_similarity_search: boolean;
    can_add_documents: boolean;
  };
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8001') {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck(): Promise<APIResponse> {
    return this.request('/health');
  }

  // Vector store status
  async getVectorStoreStatus(): Promise<APIResponse> {
    return this.request('/api/vector-store/status');
  }

  // Vector store statistics
  async getVectorStoreStats(): Promise<APIResponse<VectorStoreStats>> {
    return this.request('/api/vector-store/stats');
  }

  // Upload RFP document
  async uploadRFP(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/api/upload-rfp`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    return response.json();
  }

  // Get requirements for a session
  async getRequirements(sessionId: string): Promise<APIResponse> {
    return this.request(`/api/requirements/${sessionId}`);
  }

  // Direct query
  async directQuery(query: QueryRequest): Promise<APIResponse> {
    return this.request('/api/query', {
      method: 'POST',
      body: JSON.stringify(query),
    });
  }

  // Generate responses
  async generateResponses(request: GenerateResponsesRequest): Promise<APIResponse> {
    return this.request('/api/generate-responses', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Get responses for a session
  async getResponses(sessionId: string): Promise<APIResponse> {
    return this.request(`/api/responses/${sessionId}`);
  }

  // Index RFP responses (Knowledge Base)
  async indexRFPResponses(file: File): Promise<APIResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/api/index-responses`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Indexing failed: ${response.status}`);
    }

    return response.json();
  }

  // Upload historical data (Knowledge Base)
  async uploadHistoricalData(files: File[], description?: string): Promise<APIResponse> {
    const formData = new FormData();
    
    files.forEach(file => {
      formData.append('files', file);
    });
    
    if (description) {
      formData.append('description', description);
    }

    const response = await fetch(`${this.baseURL}/api/upload-historical-data`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Historical data upload failed: ${response.status}`);
    }

    return response.json();
  }

  // Clean up session
  async cleanupSession(sessionId: string): Promise<APIResponse> {
    return this.request(`/api/session/${sessionId}`, {
      method: 'DELETE',
    });
  }
}

// Create singleton instance
export const apiClient = new APIClient();

// Export for custom base URLs
export { APIClient };