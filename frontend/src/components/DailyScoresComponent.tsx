import { useState, useEffect } from "react";

import { api } from '@/services/api';
import type { Game, Score} from "@/services/api";
import { GameScorecard } from "./GameScorecardComponent";

export function DailyScores() {
    // date selector with default date
    // set up state variables
    const [games, setGames] = useState<Game[]>([]);
    const [scores, setScores] = useState<Score[]>([]);
    const [error, setError] = useState<Error | null>(null);
    const [loading, setLoading] = useState(true);

    // load data from the get scores end point
    useEffect(() => {
        const fetchData = async () => {
            try {
                const today = '2025-12-01' //new Date().toISOString().split('T')[0];
                const result = await api.getDailyScoreboard(today);

                setGames(result.games);
                setScores(result.scores);
            } catch (err) {
                if (err instanceof Error) {
                    setError(err);
                }
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);
    
    if (loading) return <div>Loading...</div>
    if (error) return <div>Error: {error.message}</div>
    if (games.length === 0 || scores.length === 0) return <div>No data available</div>
    
    // display daily scores
    return (
        <div className="space-y-4">
            {games.map(game => (
                <GameScorecard 
                    key={game.name}
                    game={game}
                    scores={scores.filter(score => score.gameName === game.name)}
                />
            ))}
        </div>
    )
}