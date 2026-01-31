import { useState, useEffect } from "react";
import { toast } from 'react-toastify';

import { api, DuplicateError } from '@/services/api';
import type { CreateScoreRequest, Game } from "@/services/api";

interface ScoreEntryProps {
    playerName: string;
}

function getTodaysDate() {
    return new Date().toISOString().split('T')[0];
}

export function ScoreEntry({playerName}: ScoreEntryProps) {
    // set up state variables
    const [games, setGames] = useState<Game[]>([]);
    const [loading, setLoading] = useState(true);
    const [update, setUpdate] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [selectedDate, setSelectedDate] = useState<string>(getTodaysDate());
    const [selectedGame, setSelectedGame] = useState<string>('');
    const [gameScore, setGameScore] = useState<string>('');

    // load list of games
    useEffect(() => {
        api.getGames(playerName)
        .then(setGames)
        .catch(setError)
        .finally(() => {setLoading(false);});
    }, [playerName]);

    if (loading) return <div>Loading...</div>
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
        <div className="bg-white rounded-lg shadow-md p-6 max-w-sm">
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
    )
}