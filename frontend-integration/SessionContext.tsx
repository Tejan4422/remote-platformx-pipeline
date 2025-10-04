// Session Context Provider for Frontend
// This file should be placed in your frontend at: src/contexts/SessionContext.tsx

import { createContext, useContext, useState, ReactNode } from 'react';

interface SessionContextType {
  sessionId: string | null;
  setSessionId: (id: string | null) => void;
  clearSession: () => void;
  hasActiveSession: boolean;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export const SessionProvider = ({ children }: { children: ReactNode }) => {
  const [sessionId, setSessionIdState] = useState<string | null>(
    typeof window !== 'undefined' ? localStorage.getItem('currentSessionId') : null
  );

  const setSessionId = (id: string | null) => {
    setSessionIdState(id);
    if (typeof window !== 'undefined') {
      if (id) {
        localStorage.setItem('currentSessionId', id);
      } else {
        localStorage.removeItem('currentSessionId');
      }
    }
  };

  const clearSession = () => setSessionId(null);

  const hasActiveSession = Boolean(sessionId);

  return (
    <SessionContext.Provider value={{ 
      sessionId, 
      setSessionId, 
      clearSession, 
      hasActiveSession 
    }}>
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within SessionProvider');
  }
  return context;
};