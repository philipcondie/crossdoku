import { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";
import { toast } from 'react-toastify';

import { api, DuplicateError } from '@/services/api';
import type { CreateScoreRequest, Game } from "@/services/api";
import { Spinner } from "./SpinnerComponent";
import { useAuth } from "@/context/AuthContext";


function getTodaysDate(): string {
    const now = new Date();
    const currentHour = parseInt(
        now.toLocaleString('en-US', {timeZone: 'America/New_York',hour:'numeric',hour12:false})
    );

    const today = now.toLocaleString('en-US', {
        timeZone: 'America/New_York',
        weekday: 'long' // 'Monday', 'Tuesday', etc.
    });

    // Helper: formats a Date as 'YYYY-MM-DD' in Eastern time
    const formatEastern = (date: Date): string =>
        date.toLocaleDateString('en-CA', { timeZone: 'America/New_York' });

    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    if (today === 'Saturday' && currentHour >= 18){
        return formatEastern(tomorrow);
    } else if (currentHour >= 22) {
        return formatEastern(tomorrow);
    }
    return formatEastern(now);
}

export function ScoreEntry() {
    const {playerName} = useAuth();
    // set up state variables
    const [games, setGames] = useState<Game[]>([]);
    const [loading, setLoading] = useState(true);
    const [update, setUpdate] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [selectedDate, setSelectedDate] = useState<string>(getTodaysDate());
    const [selectedGame, setSelectedGame] = useState<string>('');
    const [gameScore, setGameScore] = useState<string>('');

    if (!playerName) {
        return <Navigate to='/login'/>
    }

    // load list of games
    useEffect(() => {
        api.getGames(playerName)
        .then(setGames)
        .catch(setError)
        .finally(() => {setLoading(false);});
    }, [playerName]);

    if (loading) return <Spinner />
    if (error) return <div>{error.message} Bad Player Name: {playerName}</div>

    const handleSubmit = async () => {
        const scoreRequest: CreateScoreRequest = {
            playerName: playerName,
            gameName: selectedGame,
            date: selectedDate,
            score: Number(gameScore),
        };

        try {
            await api.createScore(scoreRequest);
            // update UI
            toast.success('Score Saved!')
            setSelectedDate(getTodaysDate());
            setSelectedGame('');
            setGameScore('');
        } catch (error) {
            if (error instanceof DuplicateError){
                toast.error("DUPLICATE")
                setUpdate(true);
            } else {
                console.error('Error creating score:', error);
                const message = error instanceof Error ? error.message : "Failed to save score"
                toast.error(message)
            }
        }
    };

    const handleUpdate = async () => {
        const scoreRequest: CreateScoreRequest = {
            playerName: playerName,
            gameName: selectedGame,
            date: selectedDate,
            score: Number(gameScore),
        };

        try {
            await api.updateScore(scoreRequest);
            // update UI
            toast.success('Score Updated!')
            setSelectedDate(getTodaysDate());
            setSelectedGame('');
            setGameScore('');
            setUpdate(false);
        } catch (error) {                    
            console.error('Error creating score:', error);
            const message = error instanceof Error ? error.message : "Failed to save score"
            toast.error(message)            
        }
    }

    return (
        <>
            <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 max-w-sm">
                <form onSubmit={(e)=>{ e.preventDefault(); update ? handleUpdate() : handleSubmit();}}>
                    <div className="mb-4">
                        <label className="block mb-2 font-medium">Date</label>
                        <input 
                            className="border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer" 
                            type="date" 
                            required
                            value={selectedDate}
                            onChange={(e) => {setSelectedDate(e.target.value); setUpdate(false);}}
                        />
                    </div>
                    <div className="mb-4">
                        <label className="block mb-2 font-medium">Game</label>            
                        <select 
                            className="border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white cursor-pointer" 
                            required
                            value={selectedGame}
                            onChange={(e) => {setSelectedGame(e.target.value); setUpdate(false);}}
                        >
                            <option value="">Select Game</option>
                            {games.map((game) => (
                                <option key={game.id} value={game.name}>{game.name}</option>
                            ))}
                        </select>
                    </div>
                    <div className="mb-4">
                        <label className="block mb-2 font-medium">Score</label>        
                        <input 
                            className="border border-gray-300 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer" 
                            type="number" 
                            placeholder="Enter score here..." 
                            required 
                            value={gameScore}
                            onChange={(e) => setGameScore(e.target.value)}
                        />                    
                    </div>
                    <div className="mt-4 text-right">
                        <button type="submit" className="bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded">{update? 'Update' : 'Save'}</button>                     
                    </div>
                </form>
            </div>
        </>
    )
}