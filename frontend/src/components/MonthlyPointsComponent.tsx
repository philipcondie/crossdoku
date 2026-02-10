import { useState, useEffect, useMemo } from "react";

import { api } from '@/services/api';
import type { Player, Point} from "@/services/api";
import { Spinner } from "./SpinnerComponent";
import { DateNavigator } from "./DateNavigatorComponent";

export function MonthlyPoints() {
    // create state variables (players, games, points, loading, error)
    const [players, setPlayers] = useState<Player[]>([]);
    const [categories, setCategories] = useState<string[]>([]);
    const [games, setGames] = useState<string[]>([]);
    const [points, setPoints] = useState<Point[]>([]);
    const [error, setError] = useState<Error | null>(null);
    const [loading, setLoading] = useState(true);
    const dateDefault = new Date('2026-01-31T00:00:00');
    const [date, setDate] = useState<Date>(dateDefault); // new Date().toISOString().split('T')[0];

    // load data
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            setError(null);
            try {
                const dateString = date.toISOString().split('T')[0];
                const result = await api.getMonthlyScores(dateString);

                setPlayers(result.players);
                setCategories(result.categories);
                setPoints(result.playerPoints);
                setGames(result.games);
                if (result.players.length === 0 || result.categories.length === 0 || result.games.length === 0 || result.playerPoints.length === 0) {
                    setError(Error('No valid scores for this date'))
                }
            } catch (err){
                if (err instanceof Error) {
                    setError(err);
                }
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [date]);

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

    const getSortedPlayers = (category: string): Player[] => {
        // create list of the scores for that category
        let points = new Map();
        for (const player of players) {
            points.set(player,getPoint(category,player.name));
        }

        const sortedPlayers = [...points.entries()]
            .sort((a,b) => {
                const valA = a[1];
                const valB = b[1];

                if (valA === '-' && valB === '-') return 0;
                if (valA === '-') return 1;
                if (valB === '-') return -1;
                return valB - valA;
            })
            .map(([key]) => key);
        return sortedPlayers;
    }

    const categoryDisplayNames: Record<string, string> = {
        "Participation": "Part.",
        "Individual": "Ind.",
        "Combined": "Comb.",
        "Total": "Total"
    };
    // create display
    if (loading) return <Spinner />

    const updateDate = (change: number) => {
        const newDate = new Date(date);
        newDate.setDate(newDate.getDate() + change);
        setDate(newDate);
    }

    return (
        <>
            <div  className="space-y-4">
                <DateNavigator currentDate={date} onDateChange={updateDate} />
                {error &&
                    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 max-w-sm">
                        Error: {error.message}
                    </div>
                }

                {!error &&
                    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 max-w-sm">
                        <h2 className="text-xl font-bold mb-3">Points</h2>
                        <div className="flex justify-between items-center py-2 border-b border-gray-200">
                            <p className="flex-2 font-bold"></p>         
                            {categories.map(category => (
                                <p key={category} className="flex-1 font-bold">{categoryDisplayNames[category]}</p>
                            ))}
                        </div>
                        {getSortedPlayers("Total").map(player => (
                            <div key={player.name} className="flex justify-between items-center py-2 border-b border-gray-200">
                                <p className="flex-2">{player.name}</p>
                                {categories.map(category => (
                                    <p key={category} className="flex-1">{getPoint(category,player.name)}</p>
                                ))}
                            </div>
                        ))}
                    </div>}
                {!error && games.map(game => (
                    <div 
                        className="bg-white rounded-lg shadow-md p-6 max-w-sm"
                        key={game}
                    >
                        <h2 className="text-xl font-bold mb-3">{game}</h2>
                        {getSortedPlayers(game).map(player => (
                            <div key={player.name} className="flex justify-between items-center py-2 border-b border-gray-200"> {/* Row */}
                                <p className="flex-1">{player.name}</p> {/* Cell one */}
                                <p className="font-bold ml-4">{getPoint(game,player.name)}</p> {/* Cell two */}
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </>
    );
}