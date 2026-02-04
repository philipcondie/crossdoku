import { useAuth } from "@/context/AuthContext";
import { Outlet, Navigate } from "react-router-dom";


export function ProtectedRoute() {
    const {isAuthenticated, playerName} = useAuth();
    if (!isAuthenticated || !playerName) {
        return <Navigate to='/login' />
    }

    return <Outlet />
}