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
            <div className="bg-gray-100 min-h-screen flex items-center justify-center p-4">
                <div className="bg-white rounded-xl shadow-md border border-gray-200 flex flex-col min-h-100 w-full max-w-md items-center justify-center">
                    <div className='w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-300 rounded-2xl flex items-center justify-center mb-6 text-white   
  text-3xl font-bold'>C</div>
                    <form className='w-full p-5' onSubmit={handleSelect}>
                        <select 
                            onChange={(e) => {setSelectedPlayer(e.target.value)}} 
                            value={selectedPlayer} 
                            required
                            className="border border-gray-300 rounded-lg px-4 py-3.5 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-text"
                            >
                            <option value="">Select Player</option>
                            {players.map((player) => (
                                <option key={player.id} value={player.name}>{player.name}</option>
                            ))}
                        </select>
                        <div className="mt-4 text-right">
                            <button type='submit' className="bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold w-full py-3.5">Select</button>                     
                        </div>
                    </form>
                </div>
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
        <div className="bg-gray-100 min-h-screen flex items-center justify-center p-4">
            <div className="bg-white rounded-xl shadow-md border border-gray-200 flex flex-col min-h-100 w-full max-w-md items-center justify-center">
                <div className='w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-300 rounded-2xl flex items-center justify-center mb-6 text-white   
  text-3xl font-bold'>C</div>
                <h2 className="text-2xl mb-2 text-zinc-700">Crossdoku</h2>
                <form className='w-full p-5' onSubmit={handleSubmit}>
                    <label className="block mb-2 font-medium">Password</label>
                    <input
                            className="border border-gray-300 rounded-lg px-4 py-3.5 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-text"
                            required
                            type='password'
                            placeholder='Enter the password'
                            onChange={(e)=>{setPassword(e.target.value);setError("");}}
                    />
                    <div className="mt-4">
                        <button type="submit" className="bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold w-full py-3.5">Login</button>
                    </div>
                    <div className='mt-4'>
                        {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
                    </div>
                </form>
            </div>
        </div>
    )
}