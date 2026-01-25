export interface Player {
    id?: number;
    name: string
}

export type ScoreMethod = 1 | -1

export interface Game {
    id?: number;
    name: string;
    scoringMethod: ScoreMethod;
}

export interface Player {
    id?: number;
    name: string;
}

export interface Score {
    id?: number;
    playerName: string;
    gameName: string;
    date: string; // YYYY-MM-DD
    score: number;
}

export interface Point {
    playerName: string;
    category: string;
    points: number;
}

export interface CreateScoreRequest {
    playerName: string;
    gameName: string;
    date: string; // YYYY-MM-DD
    score: number;
}

export interface DailyScoreboard {
    date: string;
    players: Player[];
    games: Game[];
    scores: Score[];
}

export interface MonthlyScoreboard {
    players: Player[];
    categories: string;
    points: Point[];
}