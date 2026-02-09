import { useState, useEffect } from "react";

import { api } from '@/services/api';
import type { Game, Score} from "@/services/api";
import { GameScorecard } from "./GameScorecardComponent";
import { Spinner } from "./SpinnerComponent";
import {DateNavigator} from "@/components/DateNavigatorComponent";

export function DailyScores() {
    // date selector with default date
    // set up state variables
    const [games, setGames] = useState<Game[]>([]);
    const [scores, setScores] = useState<Score[]>([]);
    const [error, setError] = useState<Error | null>(null);
    const [loading, setLoading] = useState<Boolean>(true);
    const dateDefault = new Date('2026-01-31T00:00:00');
    const [date, setDate] = useState<Date>(dateDefault); // new Date().toISOString().split('T')[0];

    // load data from the get scores end point
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const dateString = date.toISOString().split('T')[0];
                const result = await api.getDailyScoreboard(dateString);
                setGames(result.games);
                setScores(result.scores);
                if (result.games.length === 0 || result.scores.length === 0) {
                    setError(Error('No data for this date'));
                }
            } catch (err) {
                if (err instanceof Error) {
                    setError(err);
                }
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [date]);

    if (loading) return <Spinner />

    const updateDate = (change: number) => {
        const newDate = new Date(date);
        newDate.setDate(newDate.getDate() + change);
        setDate(newDate);
    }
    
    // display daily scores
    return (
        <>
            <div className="space-y-4">
                <DateNavigator currentDate={date} onDateChange={updateDate} />
                {error &&
                    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 max-w-sm">
                        Error: {error.message}
                    </div>}
                {!error && games.map(game => (
                    <GameScorecard 
                        key={game.name}
                        game={game}
                        scores={scores.filter(score => score.gameName === game.name)}
                    />
                ))}
            </div>
        </>
    )
}
