import { useState, useEffect, useMemo } from "react";

import { api } from '@/services/api';
import type { Player, Point} from "@/services/api";
import { Spinner } from "./SpinnerComponent";

export function MonthlyPoints() {
    // create state variables (players, games, points, loading, error)
    const [players, setPlayers] = useState<Player[]>([]);
    const [categories, setCategories] = useState<string[]>([]);
    const [games, setGames] = useState<string[]>([]);
    const [points, setPoints] = useState<Point[]>([]);
    const [error, setError] = useState<Error | null>(null);
    const [loading, setLoading] = useState(true);

    // load data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const today = '2025-12-25' // new Date().toISOString().split('T')[0];
                const result = await api.getMonthlyScores(today);
                console.log(result);

                setPlayers(result.players);
                setCategories(result.categories);
                setPoints(result.playerPoints);
                setGames(result.games);
            } catch (err){
                if (err instanceof Error) {
                    setError(err);
                }
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // create map for data
    const pointMap = useMemo(() => {
        if (loading || error || !points.length) {
            return new Map();
        }
        return new Map(
            points.map(point => [`${point.category}-${point.playerName}`, point])
        );
    }, [points, loading, error]);

    const getPoint = (category: string, playerName: string) => {
        return pointMap.get(`${category}-${playerName}`)?.points ?? '-'
    }
    const categoryDisplayNames: Record<string, string> = {
        "Participation": "Part.",
        "Individual": "Ind.",
        "Combined": "Comb.",
        "Total": "Total"
    };
    // create display
    if (loading) return <Spinner />
    if (error) return <div>Error: {error.message}</div>
    if (players.length === 0 || categories.length === 0 || games.length === 0 || points.length === 0) return <div>No data available</div>

    return (
        <div  className="space-y-4">
            <div className="bg-white rounded-lg shadow-md p-6 max-w-sm">
                <h2 className="text-xl font-bold mb-3">Monthly Points</h2>
                <div className="flex justify-between items-center py-2 border-b border-gray-200">
                    <p className="flex-2 font-bold">Players</p>         
                    {categories.map(category => (
                        <p key={category} className="flex-1 font-bold">{categoryDisplayNames[category]}</p>
                    ))}
                </div>
                {players.map(player => (
                    <div key={player.name} className="flex justify-between items-center py-2 border-b border-gray-200">
                        <p className="flex-2">{player.name}</p>
                        {categories.map(category => (
                            <p key={category} className="flex-1">{getPoint(category,player.name)}</p>
                        ))}
                    </div>
                ))}
            </div>
            {games.map(game => (
                <div 
                    className="bg-white rounded-lg shadow-md p-6 max-w-sm"
                    key={game}
                >
                    <h2 className="text-xl font-bold mb-3">Monthly {game}</h2>
                    {players.map(player => (
                        <div key={player.name} className="flex justify-between items-center py-2 border-b border-gray-200"> {/* Row */}
                            <p className="flex-1">{player.name}</p> {/* Cell one */}
                            <p className="font-bold ml-4">{getPoint(game,player.name)}</p> {/* Cell two */}
                        </div>
                    ))}
                </div>
            ))}
        </div>
    );
}