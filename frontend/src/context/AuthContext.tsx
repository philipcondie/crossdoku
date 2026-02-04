import { createContext, useState, useEffect, useContext } from "react";
import { api } from '@/services/api';

interface AuthContextType {
    isAuthenticated: boolean;
    playerName: string | null;
    selectPlayer: (name: string) => void;
    login: (password: string) => Promise<boolean>;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({children} : {children: React.ReactNode}) {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [playerName, setPlayerName]  = useState<string>("");

    useEffect(() => {
        const savedAuth = localStorage.getItem('isAuthenticated');
        const savedPlayerName = localStorage.getItem('playerName');
        if (savedAuth) {
            setIsAuthenticated(true);
        }
        if (savedPlayerName) {
            setPlayerName(savedPlayerName);
        }
    }, [])

    const selectPlayer = (playerName: string) => {
        localStorage.setItem('playerName', playerName);
        setPlayerName(playerName);
    }

    const login = async (password: string) => {
        try {
            await api.verifyPassword(password);
            localStorage.setItem('isAuthenticated', "true");
            setIsAuthenticated(true);
            return true;
        } catch (error) {
            return false;
        }
        
    };

    const logout = () => {
        localStorage.removeItem('isAuthenticated');
        setIsAuthenticated(false);
        localStorage.removeItem('playerName');
        setPlayerName("");
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, playerName, selectPlayer, login, logout}}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}