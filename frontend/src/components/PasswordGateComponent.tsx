import { api } from '@/services/api';
import { useState, useEffect } from 'react';
import { Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import type { Player } from '@/services/api';


export function PasswordGate () {
    const {isAuthenticated, playerName, selectPlayer, login} = useAuth();
    const [password, setPassword] = useState<string>("");
    const [selectedPlayer, setSelectedPlayer] = useState<string>("");
    const [error, setError] = useState<string>("");
    const [players, setPlayers] = useState<Player[]>([]);
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated) {
            api.getPlayers().then(setPlayers)
        }
    }, [isAuthenticated])


    if (isAuthenticated && playerName) {
       return  <Navigate to="/score" />
    }

    const handleSelect = (e: React.FormEvent) => {
        e.preventDefault();
        selectPlayer(selectedPlayer);
        navigate("/score");
    }

    if (isAuthenticated) {
        return (
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 max-w-sm">
                <form onSubmit={handleSelect}>
                    <div className="mb-4">
                        <label className="block mb-2 font-medium">Player</label>
                        <select onChange={(e) => {setSelectedPlayer(e.target.value)}} value={selectedPlayer} required>
                            <option value="">Select Player</option>
                            {players.map((player) => (
                                <option key={player.id} value={player.name}>{player.name}</option>
                            ))}
                        </select>
                        <div className="mt-4 text-right">
                            <button type='submit' className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded">Select</button>                     
                        </div>
                    </div>
                </form>
            </div>
        )
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const success = await login(password);
        if (!success) {
            setError("Invalid password. Please try again.");
        }
    }

    return (
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 max-w-sm">
            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <label className="block mb-2 font-medium">Password</label>
                    <input 
                            className="border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"  
                            required
                            type='password'
                            onChange={(e)=>{setPassword(e.target.value);setError("");}}
                    />
                    <div className="mt-4 text-right">
                        <button type="submit" className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded">Login</button>                     
                    </div>
                    <div className='mt-4 text-left'>
                        {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
                    </div>
                </div>
            </form>
        </div>
    )
}