/**
 * Hook for managing animations
 * Handles animation generation, status checking, and history
 */

import { useState, useCallback } from 'react';
import { useAuth } from './use-auth';

interface Animation {
    _id: string;
    user_id: string;
    prompt: string;
    status: 'pending' | 'generating' | 'completed' | 'error';
    video_path?: string;
    error?: string;
    created_at: string;
    updated_at: string;
}

interface UseAnimationReturn {
    animations: Animation[];
    loading: boolean;
    error: string | null;
    generateAnimation: (prompt: string, quality?: string) => Promise<string>;
    checkStatus: (animationId: string) => Promise<Animation>;
    listAnimations: (limit?: number, skip?: number) => Promise<void>;
    deleteAnimation: (animationId: string) => Promise<void>;
    getAnimation: (animationId: string) => Promise<Animation>;
}

export function useAnimation(): UseAnimationReturn {
    const [animations, setAnimations] = useState<Animation[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const { isAuthenticated } = useAuth();

    const getToken = useCallback(() => {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            throw new Error('Not authenticated');
        }
        return token;
    }, []);

    const generateAnimation = useCallback(async (prompt: string, quality: string = 'medium'): Promise<string> => {
        if (!isAuthenticated) {
            throw new Error('Not authenticated');
        }

        setLoading(true);
        setError(null);

        try {
            const token = getToken();
            const response = await fetch('http://localhost:5000/api/animations/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ prompt, quality })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'Failed to generate animation');
            }

            const data = await response.json();
            return data.animation_id;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to generate animation';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [isAuthenticated, getToken]);

    const checkStatus = useCallback(async (animationId: string): Promise<Animation> => {
        if (!isAuthenticated) {
            throw new Error('Not authenticated');
        }

        try {
            const token = getToken();
            const response = await fetch(`http://localhost:5000/api/animations/status/${animationId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'Failed to check animation status');
            }

            const data = await response.json();
            return data;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to check animation status';
            setError(message);
            throw err;
        }
    }, [isAuthenticated, getToken]);

    const listAnimations = useCallback(async (limit: number = 10, skip: number = 0): Promise<void> => {
        if (!isAuthenticated) {
            throw new Error('Not authenticated');
        }

        setLoading(true);
        setError(null);

        try {
            const token = getToken();
            const response = await fetch(`http://localhost:5000/api/animations/list?limit=${limit}&skip=${skip}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'Failed to list animations');
            }

            const data = await response.json();
            setAnimations(data.animations);
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to list animations';
            setError(message);
        } finally {
            setLoading(false);
        }
    }, [isAuthenticated, getToken]);

    const deleteAnimation = useCallback(async (animationId: string): Promise<void> => {
        if (!isAuthenticated) {
            throw new Error('Not authenticated');
        }

        setLoading(true);
        setError(null);

        try {
            const token = getToken();
            const response = await fetch(`http://localhost:5000/api/animations/${animationId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'Failed to delete animation');
            }

            // Remove animation from state
            setAnimations(prev => prev.filter(a => a._id !== animationId));
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to delete animation';
            setError(message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [isAuthenticated, getToken]);

    const getAnimation = useCallback(async (animationId: string): Promise<Animation> => {
        if (!isAuthenticated) {
            throw new Error('Not authenticated');
        }

        try {
            const token = getToken();
            const response = await fetch(`http://localhost:5000/api/animations/${animationId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'Failed to get animation');
            }

            const data = await response.json();
            return data;
        } catch (err) {
            const message = err instanceof Error ? err.message : 'Failed to get animation';
            setError(message);
            throw err;
        }
    }, [isAuthenticated, getToken]);

    return {
        animations,
        loading,
        error,
        generateAnimation,
        checkStatus,
        listAnimations,
        deleteAnimation,
        getAnimation,
    };
} 