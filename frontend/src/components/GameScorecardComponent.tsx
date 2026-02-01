import type { Game, Score} from "@/services/api";

interface GameScorecardProps{
    game: Game,
    scores: Score[]
}
export function GameScorecard({game, scores}:GameScorecardProps) {
    return (
        <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6 max-w-sm"> {/* Outer Container*/}
         <h2 className="text-xl font-bold mb-3">{game.name}</h2>
         {
            scores.map(score => (
                <div key={score.playerName} className="flex justify-between items-center py-2 border-b border-gray-200"> {/* Row */}
                    <p className="flex-1">{score.playerName}</p> {/* Cell one */}
                    <p className="font-bold ml-4">{score.score}</p> {/* Cell two */}
                </div>
            ))
         }
        </div>
    )
}